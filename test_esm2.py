# test_esm2.py
import torch
import esm

print("🧬 Testing ESM2 model loading...")

# Load the smallest ESM2 model for testing
model, alphabet = esm.pretrained.esm2_t6_8M_UR50D()
batch_converter = alphabet.get_batch_converter()

print("✅ ESM2 model loaded successfully!")
print(f"Model size: ~8M parameters")
print(f"Embedding dimension: {model.embed_dim}")

# Test with a simple protein sequence
data = [("test_protein", "MKTAYIAKQRQ")]
batch_labels, batch_strs, batch_tokens = batch_converter(data)

with torch.no_grad():
    results = model(batch_tokens, repr_layers=[6], return_contacts=False)
    embeddings = results["representations"][6]
    
print(f"✅ Generated embedding shape: {embeddings.shape}")
print("🎉 ESM2 is working perfectly!")