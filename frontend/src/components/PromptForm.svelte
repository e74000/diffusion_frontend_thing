<script>
  import { writable } from 'svelte/store';
  import TextField from './TextField.svelte';
  import ImageGallery from './ImageGallery.svelte';
  import InfoButton from './InfoButton.svelte'

  let prompt = '1boy, green hair, sweater, looking at viewer, upper body, beanie, outdoors, night, turtleneck, masterpiece, best quality, very aesthetic, absurdes';
  let negativePrompt = 'nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, oldest, early, chromatic aberration, artistic error, scan, [abstract]';
  let aspectRatio = '1:1';
  let working = false;
  let jobId = writable(null);
  let status = writable(null);
  let progress = writable(0);
  let queuePosition = writable(null);
  let images = writable([]);

  const aspectRatios = ['1:1', '9:7', '7:9', '19:13', '13:19', '7:4', '4:7', '12:5', '5:12'];

  function handleSubmit() {
    working = true;
    fetch('http://localhost:8080/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, negative_prompt: negativePrompt, aspect_ratio: aspectRatio })
    })
      .then(response => response.json())
      .then(data => {
        jobId.set(data.job_id);
        pollStatus(data.job_id);
      })
      .catch(error => console.error('Error:', error));
  }

  function pollStatus(jobId) {
    const interval = setInterval(() => {
      fetch(`http://localhost:8080/status/${jobId}`)
        .then(response => response.json())
        .then(data => {
          status.set(data.status);
          if (data.status === 'in_queue') {
            queuePosition.set(data.position);
          } else if (data.status === 'generating') {
            queuePosition.set(null);
            progress.set(data.progress);
          } else if (data.status === 'complete') {
            clearInterval(interval);
            fetchResult(jobId);
            working = false;
          } else if (data.status === 'failed') {
            clearInterval(interval);
            console.error('Job failed');
            working = false;
          }
        })
        .catch(error => console.error('Error:', error));
    }, 1000);
  }

  function fetchResult(jobId) {
    fetch(`http://localhost:8080/result/${jobId}`)
      .then(response => response.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        images.update(imgs => [...imgs, url]);
      })
      .catch(error => console.error('Error:', error));
  }

  function correctTags() {
    const tagsToCorrect = prompt + ',' + negativePrompt;
    fetch('http://localhost:8080/correct_tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags: tagsToCorrect })
    })
      .then(response => response.json())
      .then(data => {
        const [correctedPromptTags, correctedNegativePromptTags] = splitTags(data.corrected_tags);
        prompt = correctedPromptTags.join(', ');
        negativePrompt = correctedNegativePromptTags.join(', ');
      })
      .catch(error => console.error('Error:', error));
  }

  async function fetchPromptSuggestions(query) {
    const response = await fetch(`http://localhost:8080/autocomplete_tag?tag=${query}`);
    return await response.json();
  }

  async function fetchNegativePromptSuggestions(query) {
    const response = await fetch(`http://localhost:8080/autocomplete_tag?tag=${query}`);
    return await response.json();
  }

  function splitTags(tags) {
    const promptTags = [];
    const negativePromptTags = [];
    tags.forEach(tag => {
      if (prompt.includes(tag)) {
        promptTags.push(tag);
      } else {
        negativePromptTags.push(tag);
      }
    });
    return [promptTags, negativePromptTags];
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4 mx-auto max-w-xl">
  <TextField
    label="prompt"
    id="prompt"
    bind:value={prompt}
    placeholder="enter your prompt"
    autocompleteFunction={fetchPromptSuggestions}
  />

  <TextField
    label="negative prompt"
    id="negativePrompt"
    bind:value={negativePrompt}
    placeholder="enter your negative prompt"
    autocompleteFunction={fetchNegativePromptSuggestions}
  />

  <div>
    <label for="aspectRatio" class="block text-sm font-medium text-gray-700">aspect ratio</label>
    <select id="aspectRatio" bind:value={aspectRatio} class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2">
      {#each aspectRatios as ratio}
        <option value={ratio}>{ratio}</option>
      {/each}
    </select>
  </div>

  <div class="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0 sm:space-x-4">
    <div class="flex items-center space-x-2">
      <button type="submit" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300" disabled={working} title="Generate an image using the specified parameters.">
        <i class="ri-brush-line mr-2 text-xl"></i>
        generate
      </button>
  
      <button type="button" on:click={correctTags} class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" title="Attempt to correct tags using a semantic similarity search. Tags don't necessarily need to be valid to work, but valid tags more often produce good results.">
        <i class="ri-sparkling-line text-xl"></i>
      </button>
    </div>
  
    <div class="flex items-center space-x-4 ml-auto w-full sm:w-auto justify-center sm:justify-end">
      {#if $status === 'in_queue'}
        <div class="flex flex-col items-center sm:flex-row sm:items-center sm:space-x-2">
          <span class="text-sm text-gray-700 w-fit">queue position: {$queuePosition}</span>
          <div class="w-5 bg-gray-200 rounded-full h-5 pulsating-bar">
            <div class="bg-indigo-600 h-5 rounded-full transition-all duration-500" style="width: 100%;"></div>
          </div>
        </div>
      {/if}
  
      {#if $status === 'generating'}
        <div class="flex items-center space-x-2 w-full sm:w-52">
          <div class="w-full sm:w-52 bg-gray-200 rounded-full h-5 pulsating-bar">
            <div class="bg-indigo-600 h-5 rounded-full transition-all duration-500" style="width: {$progress}%;"></div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</form>

<ImageGallery gap={16} maxColumnWidth={200} hover={true} loading="lazy" class="mt-4 mx-auto">
  {#each $images as img}
    <img src={img} alt="Generated Image" />
  {/each}
</ImageGallery>

<InfoButton>
  <h2 class="text-lg font-semibold mb-2">info</h2>
  <p class="text-sm text-gray-600"> this page is a simple frontend wrapper for <a href="https://cagliostrolab.net/posts/animagine-xl-v31-release" class="text-indigo-600"> animagine-xl-3.1 </a>, that <a href="e74000.net" class="text-indigo-600"> i </a> built to test out a simple semantic tag-correction system. </p>
  <p class="text-sm text-gray-600"> it supports tag autocompletion and also autocorrection of tags, by pressing the ✨button✨ below. </p>
  <p class="text-sm text-gray-600"> if for some reason you like this project and would like to add more features to it, feel free to make a pull request on the project's <a href="?" class="text-indigo-600"> github repository </a>. </p>
</InfoButton>

<style>
  .pulsating-bar {
    position: relative;
    overflow: hidden;
  }

  .pulsating-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.2) 50%, rgba(255, 255, 255, 0) 100%);
    animation: wave 1.5s infinite;
  }

  @keyframes wave {
    from {
      left: -100%;
    }
    to {
      left: 100%;
    }
  }
</style>
