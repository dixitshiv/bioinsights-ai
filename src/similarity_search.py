# src/similarity_search_fixed.py
import faiss
import numpy as np
import pandas as pd
import pickle
import torch
import esm
from typing import List, Dict, Tuple
import time
import warnings
warnings.filterwarnings('ignore')

class ProteinSimilaritySearch:
    """Fast protein similarity search using FAISS"""
    
    def __init__(self, embeddings_file="models/embeddings_for_faiss.pkl", load_esm2=False):
        """Initialize FAISS search engine"""
        
        print("🔍 Initializing Protein Similarity Search...")
        
        # Load embeddings and metadata
        with open(embeddings_file, "rb") as f:
            data = pickle.load(f)
        
        self.embeddings = data['embeddings']
        self.protein_ids = data['protein_ids']
        self.metadata = data['metadata']
        
        # Create protein metadata lookup
        self.protein_lookup = {pid: meta for pid, meta in zip(self.protein_ids, self.metadata)}
        
        print(f"✅ Loaded {len(self.protein_ids)} proteins")
        print(f"✅ Embedding dimension: {self.embeddings.shape[1]}")
        
        # Build FAISS index
        self._build_faiss_index()
        
        # Only load ESM2 if explicitly requested
        self.model = None
        self.alphabet = None
        self.batch_converter = None
        
        if load_esm2:
            self._load_esm2_model()
        
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        
        print("🏗️  Building FAISS index...")
        
        # Normalize embeddings for cosine similarity
        embeddings_normalized = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        
        # Create FAISS index
        dimension = embeddings_normalized.shape[1]
        
        # Use IndexFlatIP for exact cosine similarity (Inner Product after normalization)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to index
        self.index.add(embeddings_normalized.astype('float32'))
        
        print(f"✅ FAISS index built with {self.index.ntotal} vectors")
        print(f"✅ Index type: {type(self.index).__name__}")
        
    def _load_esm2_model(self):
        """Load ESM2 model for processing new sequences (only when needed)"""
        
        print("🧬 Loading ESM2 model for new sequence processing...")
        
        try:
            # Force CPU usage to avoid segfault
            torch.set_num_threads(1)
            
            self.model, self.alphabet = esm.pretrained.esm2_t6_8M_UR50D()
            self.batch_converter = self.alphabet.get_batch_converter()
            self.model.eval()
            
            # Force CPU usage
            self.device = torch.device("cpu")
            self.model = self.model.to(self.device)
            
            print(f"✅ ESM2 model ready on {self.device}")
            
        except Exception as e:
            print(f"❌ Error loading ESM2 model: {e}")
            print("⚠️  ESM2 model not available - can only search with pre-computed embeddings")
            self.model = None
    
    def embed_sequence(self, sequence: str, protein_name: str = "query") -> np.ndarray:
        """Generate embedding for a new protein sequence"""
        
        if self.model is None:
            print("⚠️  ESM2 model not loaded. Loading now...")
            self._load_esm2_model()
            
        if self.model is None:
            raise RuntimeError("ESM2 model could not be loaded. Use pre-computed embeddings only.")
        
        # Prepare data for model
        data = [(protein_name, sequence)]
        batch_labels, batch_strs, batch_tokens = self.batch_converter(data)
        batch_tokens = batch_tokens.to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            results = self.model(batch_tokens, repr_layers=[self.model.num_layers])
            token_representations = results["representations"][self.model.num_layers]
            sequence_representation = token_representations[0, 1:-1].mean(0)
            
        return sequence_representation.cpu().numpy()
    
    def search_similar(self, 
                      query_sequence: str = None,
                      query_embedding: np.ndarray = None,
                      query_protein_id: str = None,
                      top_k: int = 5,
                      min_similarity: float = 0.0,
                      filter_chain_type: str = None,
                      filter_therapeutic_area: str = None) -> List[Dict]:
        """
        Search for similar proteins
        
        Args:
            query_sequence: Protein sequence to search (requires ESM2 model)
            query_embedding: Pre-computed embedding
            query_protein_id: Use embedding from existing protein in database
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            filter_chain_type: Filter by 'heavy' or 'light' chains
            filter_therapeutic_area: Filter by therapeutic area
        """
        
        start_time = time.time()
        
        # Get query embedding
        if query_protein_id is not None:
            # Use existing protein from database
            if query_protein_id not in self.protein_ids:
                raise ValueError(f"Protein ID {query_protein_id} not found in database")
            idx = self.protein_ids.index(query_protein_id)
            query_embedding = self.embeddings[idx]
            print(f"🔍 Using embedding from database protein: {query_protein_id}")
            
        elif query_sequence is not None:
            print(f"🧬 Generating embedding for query sequence ({len(query_sequence)} aa)...")
            query_embedding = self.embed_sequence(query_sequence)
            
        elif query_embedding is None:
            raise ValueError("Must provide either query_sequence, query_embedding, or query_protein_id")
        
        # Normalize query embedding
        query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
        query_embedding_norm = query_embedding_norm.astype('float32').reshape(1, -1)
        
        # Search FAISS index
        similarities, indices = self.index.search(query_embedding_norm, min(top_k * 3, len(self.protein_ids)))
        
        # Process results
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
                
            protein_id = self.protein_ids[idx]
            metadata = self.protein_lookup[protein_id]
            
            # Apply filters
            if filter_chain_type and metadata['chain_type'] != filter_chain_type:
                continue
                
            if filter_therapeutic_area and metadata.get('therapeutic_area') != filter_therapeutic_area:
                continue
                
            if sim < min_similarity:
                continue
            
            result = {
                'protein_id': protein_id,
                'similarity': float(sim),
                'drug_name': metadata['drug_name'],
                'chain_type': metadata['chain_type'],
                'therapeutic_area': metadata.get('therapeutic_area', 'Unknown'),
                'metadata': metadata
            }
            results.append(result)
            
            if len(results) >= top_k:
                break
        
        search_time = time.time() - start_time
        
        print(f"✅ Found {len(results)} similar proteins in {search_time:.3f}s")
        
        return results
    
    def get_protein_info(self, protein_id: str) -> Dict:
        """Get detailed information about a protein"""
        
        if protein_id not in self.protein_lookup:
            return None
            
        return self.protein_lookup[protein_id]
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the protein database"""
        
        stats = {
            'total_proteins': len(self.protein_ids),
            'unique_drugs': len(set([meta['drug_name'] for meta in self.metadata])),
            'chain_types': {},
            'therapeutic_areas': {},
            'embedding_dimension': self.embeddings.shape[1],
            'esm2_available': self.model is not None
        }
        
        # Count chain types
        for meta in self.metadata:
            chain_type = meta['chain_type']
            stats['chain_types'][chain_type] = stats['chain_types'].get(chain_type, 0) + 1
        
        # Count therapeutic areas
        for meta in self.metadata:
            area = meta.get('therapeutic_area', 'Unknown')
            stats['therapeutic_areas'][area] = stats['therapeutic_areas'].get(area, 0) + 1
            
        return stats

def main():
    """Test the similarity search engine WITHOUT loading ESM2"""
    
    # Initialize search engine (without ESM2 to avoid segfault)
    search_engine = ProteinSimilaritySearch(load_esm2=False)
    
    # Get database stats
    stats = search_engine.get_database_stats()
    print(f"\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    # Test with existing protein embedding (safer than new sequence)
    test_protein_id = search_engine.protein_ids[0]  # Use first protein
    
    print(f"\n🧪 Testing similarity search with existing protein:")
    print(f"Query protein: {test_protein_id}")
    
    # Search for similar proteins using existing protein
    results = search_engine.search_similar(
        query_protein_id=test_protein_id,
        top_k=5,
        min_similarity=0.0
    )
    
    print(f"\n🏆 Top Similar Proteins:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['protein_id']} ({result['drug_name']})")
        print(f"   Similarity: {result['similarity']:.3f}")
        print(f"   Chain: {result['chain_type']}")
        print(f"   Area: {result['therapeutic_area']}")
        print()
    
    # Test filtering
    print(f"🔍 Testing filtered search (heavy chains only):")
    filtered_results = search_engine.search_similar(
        query_protein_id=test_protein_id,
        top_k=3,
        filter_chain_type="heavy"
    )
    
    for i, result in enumerate(filtered_results, 1):
        print(f"{i}. {result['protein_id']} - {result['similarity']:.3f}")
    
    print(f"\n✅ Search engine working! ESM2 model can be loaded separately when needed.")
    
    return search_engine

if __name__ == "__main__":
    search_engine = main()