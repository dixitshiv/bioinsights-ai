# convert_embeddings.py
import pickle
import numpy as np
import pandas as pd

print("🔧 Converting embeddings to FAISS format...")

# Load the existing embeddings
with open("models/protein_embeddings.pkl", "rb") as f:
    embeddings_dict = pickle.load(f)

with open("models/embedding_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print(f"✅ Loaded {len(embeddings_dict)} protein embeddings")

# Load the CSV data for metadata
df = pd.read_csv("data/drugbank_biologics_expanded.csv")

# Add therapeutic area classification
def classify_therapeutic_area(indication):
    indication_lower = indication.lower()
    if 'cancer' in indication_lower or 'melanoma' in indication_lower or 'lymphoma' in indication_lower:
        return 'Oncology'
    elif 'arthritis' in indication_lower or 'crohn' in indication_lower:
        return 'Autoimmune'
    else:
        return 'Other'

df['therapeutic_area'] = df['indication'].apply(classify_therapeutic_area)
df['sequence_length'] = df['sequence'].apply(len)

# Convert to format needed by FAISS search
protein_ids = list(embeddings_dict.keys())
embeddings_array = np.array([embeddings_dict[pid] for pid in protein_ids])

# Create metadata list matching the protein_ids order
metadata_list = []
for protein_id in protein_ids:
    # Parse protein ID
    parts = protein_id.split('_')
    drug_name = parts[0]
    chain_type = parts[1] if len(parts) > 1 else 'unknown'
    
    # Find matching row in DataFrame
    matching_rows = df[(df['name'] == drug_name) & (df['chain_type'] == chain_type)]
    
    if len(matching_rows) > 0:
        row = matching_rows.iloc[0]
        meta = {
            'drug_name': row['name'],
            'chain_type': row['chain_type'],
            'therapeutic_area': row['therapeutic_area'],
            'sequence': row['sequence'],
            'sequence_length': row['sequence_length'],
            'brand_name': row['brand_name'],
            'indication': row['indication'],
            'approval_year': row['approval_year'],
            'company': row['company']
        }
    else:
        # Fallback metadata
        meta = {
            'drug_name': drug_name,
            'chain_type': chain_type,
            'therapeutic_area': 'Unknown',
            'sequence': '',
            'sequence_length': 0,
            'brand_name': '',
            'indication': '',
            'approval_year': 0,
            'company': ''
        }
    
    metadata_list.append(meta)

# Create the FAISS-compatible format
faiss_data = {
    'embeddings': embeddings_array,
    'protein_ids': protein_ids,
    'metadata': metadata_list
}

# Save in the format the app expects
with open("models/embeddings_for_faiss.pkl", "wb") as f:
    pickle.dump(faiss_data, f)

print(f"✅ Created embeddings_for_faiss.pkl")
print(f"   - {len(protein_ids)} proteins")
print(f"   - Embedding shape: {embeddings_array.shape}")
print(f"   - With full metadata including therapeutic areas")

# Show sample
print(f"\n📊 Sample metadata:")
for i, meta in enumerate(metadata_list[:3]):
    print(f"  {i+1}. {meta['drug_name']} ({meta['chain_type']})")
    print(f"     Area: {meta['therapeutic_area']}")
    print(f"     Length: {meta['sequence_length']} aa")

print(f"\n🎉 Conversion complete! Ready to run the app.")
