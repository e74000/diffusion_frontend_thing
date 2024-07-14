import os
import argparse

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import threading
import queue
import uuid
import logging
import time
from io import BytesIO
import traceback

from flask import Flask, request, jsonify, send_file, send_from_directory
import torch
from diffusers import DiffusionPipeline
from PIL import Image

from tag_loader import TagLoader
from utils import strip_enclosing_characters, add_enclosing_characters

# Argument parsing for device selection
parser = argparse.ArgumentParser(description='Diffusion model server')
parser.add_argument('--device', type=str, default='mps', help='Device to use for inference (default: mps)')
args = parser.parse_args()

# Load device
try:
    device = torch.device(args.device)
    _ = torch.randn(1).to(device)  # Test if device is valid
    print(f'Using device: {device}')
except Exception as e:
    print(f'Warning: Failed to use device {args.device}, falling back to CPU. Error: {str(e)}')
    device = torch.device('cpu')

# Create Pipeline
pipe = DiffusionPipeline.from_pretrained(
    'cagliostrolab/animagine-xl-3.1',
    torch_dtype=torch.float16,
    use_safetensors=True,
).to(device)

pipe.set_progress_bar_config(disable=True)

# Create Flask App
app = Flask(__name__, static_folder='../frontend/dist')

print('Loading tags... (This may take a while)')
tag_loader = TagLoader()

# Program state
job_queue = queue.Queue()
results = {}
statuses = {}

# Supported resolutions
resolutions = {
    '1:1': (1024, 1024),
    '9:7': (1152, 896),
    '7:9': (896, 1152),
    '19:13': (1216, 832),
    '13:19': (832, 1216),
    '7:4': (1344, 768),
    '4:7': (768, 1344),
    '12:5': (1536, 640),
    '5:12': (640, 1536)
}

default_resolution = (1024, 1024)

# Pipeline config
num_steps = 12
guidance_scale = 7

def worker():
    while True:
        job_id, prompt, negative_prompt, aspect_ratio = job_queue.get()
        if job_id is None:
            break

        print(f'Processing job {job_id}')
        print(f' -> prompt:          {prompt}')
        print(f' -> negative_prompt: {negative_prompt}')
        print(f' -> aspect_ratio:    {aspect_ratio}')

        statuses[job_id] = {'status': 'generating', 'progress': 0}

        def status_callback(pipe, step, timestep, callback_kwargs):
            statuses[job_id]['progress'] = 100.0 * float(step+1) / float(num_steps)
            print(f' <- progress {100.0 * float(step+1) / float(num_steps):.2f}%')
            return callback_kwargs

        try:
            width, height = resolutions.get(aspect_ratio, default_resolution)

            img = pipe(
                prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                guidance_scale=guidance_scale,
                num_inference_steps=num_steps,
                callback_on_step_end=status_callback,
                callback_on_step_end_tensor_inputs=["latents"],
            ).images[0]

            img_io = BytesIO()
            img.save(img_io, 'png')
            img_io.seek(0)

            results[job_id] = img_io
            statuses[job_id] = {'status': 'complete'}

            print(f'job {job_id} completed successfully')
        except Exception as e:
            results[job_id] = 'internal server error'
            statuses[job_id] = {'status': 'failed'}
            print(f'error processing job {job_id}: {str(e)}')
            print(traceback.format_exc())

        job_queue.task_done()

threading.Thread(target=worker, daemon=True).start()

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    negative_prompt = request.json.get('negative_prompt', 'nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, oldest, early, chromatic aberration, artistic error, scan, [abstract]')
    aspect_ratio = request.json.get('aspect_ratio', '1:1')

    print(prompt, negative_prompt, aspect_ratio)

    job_id = uuid.uuid4().hex
    job_queue.put((
        job_id,
        prompt,
        negative_prompt,
        aspect_ratio,
    ))

    statuses[job_id] = {'status': 'in_queue', 'position': job_queue.qsize()}

    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    if job_id not in statuses:
        return jsonify({"error": "invalid job_id"}), 404

    status_info = statuses[job_id]

    if status_info["status"] == "in_queue":
        queue_list = list(job_queue.queue)
        try:
            position = queue_list.index((job_id, *queue_list[0][1:])) + 1
            status_info["position"] = position
        except ValueError:
            status_info["position"] = "job no longer in queue"

    return jsonify(status_info)

@app.route('/result/<job_id>', methods=['GET'])
def result(job_id):
    if job_id not in results:
        return jsonify({'error': 'invalid job_id'}), 404

    if statuses[job_id]['status'] == 'failed':
        return jsonify({'error': 'job failed: internal server error'}), 500

    if statuses[job_id]['status'] != 'complete':
        return jsonify({'error': 'job not yet complete, check again later'}), 400

    img_io = results[job_id]
    
    # Clean up after result is collected
    del results[job_id]
    del statuses[job_id]

    return send_file(img_io, mimetype='image/png')

@app.route('/correct_tags', methods=['POST'])
def correct_tags():
    data = request.get_json()
    tags = data['tags']
    
    corrected_tags = []
    distances = []
    for tag in tags.split(','):
        original_tag = tag.strip()
        stripped_tag = strip_enclosing_characters(original_tag)
        print(f' -> checking tag: {stripped_tag}')
        if stripped_tag in tag_loader.tags:
            print(' <- tag exists')
            corrected_tag = stripped_tag
            distance = 0.0
        else:
            closest_tag, distance = tag_loader.find_closest_tag(stripped_tag)
            print(f' <- best replacement: {closest_tag}')
            corrected_tag = closest_tag
        
        corrected_tags.append(add_enclosing_characters(corrected_tag, original_tag))
        distances.append(float(distance))
    
    return jsonify({'corrected_tags': corrected_tags, 'distances': distances})

@app.route('/autocomplete_tag', methods=['GET'])
def autocomplete_tag():
    original_tag = request.args.get('tag', '')
    
    if not original_tag:
        return jsonify({'suggestions': []})
    
    stripped_tag = strip_enclosing_characters(original_tag)
    suggestions, distances = tag_loader.find_closest_tags(stripped_tag)
    
    suggestions_with_enclosures = [add_enclosing_characters(suggestion, original_tag) for suggestion in suggestions]
    
    return jsonify({'suggestions': suggestions_with_enclosures, 'distances': distances.tolist()})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def static_proxy(path):
    if path == '':
        path = 'index.html'

    return send_from_directory(app.static_folder, path=path)

if __name__ == "__main__":
    print('starting server on port :8080')
    app.run(host="0.0.0.0", port=8080)
