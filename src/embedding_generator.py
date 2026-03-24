# src/embedding_generator.py
import torch
import esm
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
import os

class ESM2EmbeddingGenerator:
    """Generate protein embeddings using Meta's ESM2 model"""
    
    def __init__(self, model_name="esm2_t6_8M_UR50D"):
        """
        Initialize ESM2 model
        
        Available models:
        - esm2_t6_8M_UR50D: 8M parameters (fastest, good for development)
        - esm2_t12_35M_UR50D: 35M parameters (balanced)
        - esm2_t30_150M_UR50D: 150M parameters (better quality)
        - esm2_t33_650M_UR50D: 650M parameters (best quality, slowest)
        """
        print(f"🧬 Loading ESM2 model: {model_name}")
        
        # Load model and alphabet
        self.model, self.alphabet = esm.pretrained.load_model_and_alphabet(model_name)
        self.batch_converter = self.alphabet.get_batch_converter()
        self.model.eval()  # Set to evaluation mode
        
        # Move to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        
        print(f"✅ Model loaded on {self.device}")
        print(f"✅ Embedding dimension: {self.model.embed_dim}")
        
    def generate_embedding(self, sequence, protein_name="protein"):
        """Generate embedding for a single protein sequence"""
        
        # Prepare data for model
        data = [(protein_name, sequence)]
        batch_labels, batch_strs, batch_tokens = self.batch_converter(data)
        batch_tokens = batch_tokens.to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            results = self.model(batch_tokens, repr_layers=[self.model.num_layers])
            
            # Extract per-token representations
            token_representations = results["representations"][self.model.num_layers]
            
            # Take mean over sequence length (excluding special tokens)
            # Token 0 is <cls>, token -1 is <eos>
            sequence_representation = token_representations[0, 1:-1].mean(0)
            
        return sequence_representation.cpu().numpy()
    
    def generate_batch_embeddings(self, sequences_dict, batch_size=10):
        """Generate embeddings for multiple sequences efficiently"""
        
        embeddings = {}
        sequence_items = list(sequences_dict.items())
        
        print(f"🔄 Generating embeddings for {len(sequence_items)} sequences...")
        
        # Process in batches for memory efficiency
        for i in tqdm(range(0, len(sequence_items), batch_size)):
            batch_items = sequence_items[i:i+batch_size]
            
            for protein_id, sequence in batch_items:
                try:
                    embedding = self.generate_embedding(sequence, protein_id)
                    embeddings[protein_id] = embedding
                except Exception as e:
                    print(f"❌ Error processing {protein_id}: {e}")
                    # Use zero embedding as fallback
                    embeddings[protein_id] = np.zeros(self.model.embed_dim)
                    
        return embeddings

def main():
    """Generate embeddings for our drugbank biologics"""
    
    # Load data
    print("📊 Loading protein data...")
    df = pd.read_csv("data/drugbank_biologics_expanded.csv")
    
    # Create sequence dictionary
    sequences = {}
    for _, row in df.iterrows():
        protein_id = f"{row['name']}_{row['chain_type']}"
        sequences[protein_id] = row['sequence']
    
    print(f"📋 Found {len(sequences)} protein sequences to process")
    
    # Initialize embedding generator
    generator = ESM2EmbeddingGenerator()
    
    # Generate embeddings
    embeddings = generator.generate_batch_embeddings(sequences)
    
    # Save embeddings
    os.makedirs("models", exist_ok=True)
    
    # Save as pickle for fast loading
    with open("models/protein_embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)
    
    # Save metadata for reference
    embedding_metadata = {
        "model_name": "esm2_t6_8M_UR50D",
        "embedding_dim": generator.model.embed_dim,
        "num_proteins": len(embeddings),
        "protein_ids": list(embeddings.keys())
    }
    
    with open("models/embedding_metadata.pkl", "wb") as f:
        pickle.dump(embedding_metadata, f)
    
    print(f"✅ Generated embeddings for {len(embeddings)} proteins")
    print(f"✅ Embedding dimension: {generator.model.embed_dim}")
    print(f"✅ Saved to models/protein_embeddings.pkl")
    
    # Test loading
    print("\n🧪 Testing embedding loading...")
    with open("models/protein_embeddings.pkl", "rb") as f:
        loaded_embeddings = pickle.load(f)
    
    print(f"✅ Successfully loaded {len(loaded_embeddings)} embeddings")
    
    # Show sample
    sample_id = list(loaded_embeddings.keys())[0]
    sample_embedding = loaded_embeddings[sample_id]
    print(f"✅ Sample embedding shape: {sample_embedding.shape}")
    print(f"✅ Sample values: {sample_embedding[:5]}")
    
    return embeddings

if __name__ == "__main__":
    embeddings = main()