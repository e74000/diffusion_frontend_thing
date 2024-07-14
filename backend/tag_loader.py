import faiss
import numpy as np
from transformers import BertTokenizer, BertModel

# Initialize tokenizer and model globally
model_string = "bert-base-uncased"
print(f'TagLoader: Using model {model_string}')
tokenizer = BertTokenizer.from_pretrained(model_string)
print('TagLoader: Loaded tokenizer...')
model = BertModel.from_pretrained(model_string)
print('TagLoader: Loaded model...')

class TagLoader:
    def __init__(self, file_path='safe.csv'):
        self.tags, self.embeddings = self.load_tags(file_path)
        self.index = self.build_faiss_index(self.embeddings)
        del self.embeddings  # Free up memory by deleting embeddings
        import gc
        gc.collect()  # Ensure garbage collection
        print('TagLoader: Built FAISS index and disposed embeddings.')
    
    def load_tags(self, file_path):
        import pandas as pd
        df = pd.read_csv(file_path)
        tags = df['tag'].values
        embeddings = df.drop(columns=['tag']).values
        return tags, embeddings
    
    def build_faiss_index(self, embeddings):
        print("TagLoader: Building FAISS index...")
        index = faiss.IndexFlatL2(embeddings.shape[1])  # Using L2 distance
        index.add(embeddings.astype(np.float32))
        return index
    
    def find_closest_tag(self, tag, threshold=20.0):
        tag_embedding = embed_tag(tag)
        distances, indices = self.index.search(tag_embedding, 1)
        print(f'TagLoader: Checking tag {tag} got match {self.tags[indices[0][0]]} at distance {distances[0][0]}')
        if distances[0][0] < threshold:
            return self.tags[indices[0][0]], distances[0][0]
        else:
            return tag, distances[0][0]
    
    def find_closest_tags(self, tag, top_n=5):
        tag_embedding = embed_tag(tag)
        distances, indices = self.index.search(tag_embedding, top_n)
        return self.tags[indices[0]], distances[0]

def embed_tag(tag):
    inputs = tokenizer(tag, return_tensors='pt')
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()
