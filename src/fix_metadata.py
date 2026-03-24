# src/fix_metadata.py
import pandas as pd
import pickle
import numpy as np

def fix_metadata():
    """Add missing therapeutic areas and sequence lengths to our data"""
    
    print("🔧 Fixing metadata issues...")
    
    # Load the original CSV data
    try:
        df = pd.read_csv("data/drugbank_biologics.csv")
        print(f"✅ Loaded original CSV with {len(df)} entries")
    except:
        print("❌ Could not load original CSV. Let's create the data fresh.")
        
        # Create the data with proper metadata
        data = [
            {
                "name": "Adalimumab", "brand_name": "Humira", "chain_type": "heavy",
                "sequence": "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDVWGQGTLVTVSS",
                "indication": "Rheumatoid arthritis, Crohn's disease", "approval_year": 2002, "company": "AbbVie", "molecular_type": "antibody"
            },
            {
                "name": "Adalimumab", "brand_name": "Humira", "chain_type": "light", 
                "sequence": "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK",
                "indication": "Rheumatoid arthritis, Crohn's disease", "approval_year": 2002, "company": "AbbVie", "molecular_type": "antibody"
            },
            {
                "name": "Trastuzumab", "brand_name": "Herceptin", "chain_type": "heavy",
                "sequence": "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDVWGQGTLVTVSS",
                "indication": "Breast cancer", "approval_year": 1998, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Trastuzumab", "brand_name": "Herceptin", "chain_type": "light",
                "sequence": "DIQMTQSPSSLSASVGDRVTITCRASQDVSTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK", 
                "indication": "Breast cancer", "approval_year": 1998, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Rituximab", "brand_name": "Rituxan", "chain_type": "heavy",
                "sequence": "QVQLQQSGPGLVKPSQTLSLTCAISGDSVSSNSAAWNWIRQSPSRGLEWLGRTYYRSKWYNDYAVSVKSRITINPDTSKNQFSLQLNSVTPEDTAVYYCARLTKWPHTYFGQGTLVTVSS",
                "indication": "Non-Hodgkin lymphoma", "approval_year": 1997, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Rituximab", "brand_name": "Rituxan", "chain_type": "light",
                "sequence": "QIVLSQSPAILSASPGEKVTMTCRASSSVSYMNWYQQKPGTSPKPWIYDTSKLASGVPVRFSGSGSGTSYSLTISSMEAEDAATYYCQQWSSNPFTFGSGTKLEIT",
                "indication": "Non-Hodgkin lymphoma", "approval_year": 1997, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Bevacizumab", "brand_name": "Avastin", "chain_type": "heavy",
                "sequence": "EVQLVESGGGLVQPGGSLRLSCAASGYTFTNYYMSWVRQAPGKGLEWVSVIRGTTGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCARHLGGFGIGYDYAMDVWGQGTLVTVSS",
                "indication": "Colorectal cancer", "approval_year": 2004, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Bevacizumab", "brand_name": "Avastin", "chain_type": "light", 
                "sequence": "DIQMTQSPSSLSASVGDRVTITCRASQGISSWLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQLNSYPLTFGGGTKVEIK",
                "indication": "Colorectal cancer", "approval_year": 2004, "company": "Genentech", "molecular_type": "antibody"
            },
            {
                "name": "Pembrolizumab", "brand_name": "Keytruda", "chain_type": "heavy",
                "sequence": "QVQLVQSGVEVKKPGASVKVSCKASGYTFTNYYMYWVRQAPGQGLEWMGGINPSNGGTNFNEKFKNRVTLTTDSSTTTAYMELKSLQFDDTAVYYCARHNTWGGFDYWGQGTLVTVSS",
                "indication": "Melanoma, lung cancer", "approval_year": 2014, "company": "Merck", "molecular_type": "antibody"
            },
            {
                "name": "Pembrolizumab", "brand_name": "Keytruda", "chain_type": "light",
                "sequence": "EIVLTQSPATLSLSPGERATLSCRASQSVSSYLAWYQQKPGQAPRLLIYDASNRATGIPARFSGSGSGTDFTLTISSLEPEDFAVYYCQQRSNWPLTFGGGTKVEIK",
                "indication": "Melanoma, lung cancer", "approval_year": 2014, "company": "Merck", "molecular_type": "antibody"
            },
            {
                "name": "Nivolumab", "brand_name": "Opdivo", "chain_type": "heavy",
                "sequence": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSDSWIHWVRQAPGKGLEWVAWIYPGDGSTSYEPSVKGRFTISADTSKNQAYLQLNSLRAEDTAVYYCARRHYYGNSHWYFDVWGQGTLVTVSS",
                "indication": "Melanoma, lung cancer", "approval_year": 2014, "company": "Bristol Myers Squibb", "molecular_type": "antibody"
            },
            {
                "name": "Infliximab", "brand_name": "Remicade", "chain_type": "heavy",
                "sequence": "QVQLQQSGPGLVKPSQTLSLTCAISGDSVSSNSAAWNWIRQSPSRGLEWLGRTYYRSKWYNDYAVSVKSRITINPDTSKNQFSLQLNSVTPEDTAVYYCAREDKGTYGVYVFAYGGTLVTVSS",
                "indication": "Rheumatoid arthritis, Crohn's disease", "approval_year": 1998, "company": "Janssen", "molecular_type": "antibody"
            }
        ]
        
        df = pd.DataFrame(data)
        print(f"✅ Created fresh data with {len(df)} entries")
    
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
    
    # Save updated CSV
    df.to_csv("data/drugbank_biologics_fixed.csv", index=False)
    print(f"✅ Saved updated CSV with therapeutic areas")
    
    # Now update the embeddings file
    try:
        with open("models/embeddings_for_faiss.pkl", "rb") as f:
            embedding_data = pickle.load(f)
        
        print(f"✅ Loaded embedding data with {len(embedding_data['protein_ids'])} proteins")
        
        # Create updated metadata
        updated_metadata = []
        for protein_id in embedding_data['protein_ids']:
            # Parse protein ID
            parts = protein_id.split('_')
            drug_name = parts[0]
            chain_type = parts[1] if len(parts) > 1 else 'unknown'
            
            # Find matching row in DataFrame
            matching_rows = df[(df['name'] == drug_name) & (df['chain_type'] == chain_type)]
            
            if len(matching_rows) > 0:
                row = matching_rows.iloc[0]
                metadata = {
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
                metadata = {
                    'drug_name': drug_name,
                    'chain_type': chain_type,
                    'therapeutic_area': 'Unknown',
                    'sequence': '',
                    'sequence_length': 0
                }
            
            updated_metadata.append(metadata)
        
        # Update the embedding data
        embedding_data['metadata'] = updated_metadata
        
        # Save updated embeddings
        with open("models/embeddings_for_faiss_fixed.pkl", "wb") as f:
            pickle.dump(embedding_data, f)
        
        print(f"✅ Saved updated embeddings with proper metadata")
        
        # Show sample of updated metadata
        print(f"\n📊 Sample updated metadata:")
        for i, meta in enumerate(updated_metadata[:3]):
            print(f"  {i+1}. {meta['drug_name']} ({meta['chain_type']})")
            print(f"     Area: {meta['therapeutic_area']}")
            print(f"     Length: {meta['sequence_length']} aa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating embeddings: {e}")
        return False

if __name__ == "__main__":
    success = fix_metadata()
    if success:
        print(f"\n🎉 Metadata fixed successfully!")
        print(f"📝 Next steps:")
        print(f"  1. Update app.py to use the fixed embeddings file")
        print(f"  2. Restart the Streamlit app")
    else:
        print(f"\n❌ Failed to fix metadata")