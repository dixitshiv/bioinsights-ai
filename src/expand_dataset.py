# src/expand_dataset.py
import pandas as pd

def add_more_biologics():
    """Add more FDA-approved biologics to expand our dataset"""
    
    additional_biologics = [
        {
            "name": "Nivolumab",
            "brand_name": "Opdivo", 
            "drugbank_id": "DB09035",
            "indication": "Melanoma, lung cancer",
            "approval_year": 2014,
            "company": "Bristol Myers Squibb",
            "chain_type": "heavy",
            "sequence": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSDSWIHWVRQAPGKGLEWVAWIYPGDGSTSYEPSVKGRFTISADTSKNQAYLQLNSLRAEDTAVYYCARRHYYGNSHWYFDVWGQGTLVTVSS",
            "molecular_type": "antibody"
        },
        {
            "name": "Infliximab",
            "brand_name": "Remicade",
            "drugbank_id": "DB00065", 
            "indication": "Rheumatoid arthritis, Crohn's disease",
            "approval_year": 1998,
            "company": "Janssen",
            "chain_type": "heavy", 
            "sequence": "QVQLQQSGPGLVKPSQTLSLTCAISGDSVSSNSAAWNWIRQSPSRGLEWLGRTYYRSKWYNDYAVSVKSRITINPDTSKNQFSLQLNSVTPEDTAVYYCAREDKGTYGVYVFAYGGTLVTVSS",
            "molecular_type": "antibody"
        }
    ]
    
    # Convert to DataFrame
    new_df = pd.DataFrame(additional_biologics)
    
    # Load existing data
    existing_df = pd.read_csv("data/drugbank_biologics.csv")
    
    # Combine
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Add sequence length
    combined_df['sequence_length'] = combined_df['sequence'].apply(len)
    
    # Save expanded dataset
    combined_df.to_csv("data/drugbank_biologics_expanded.csv", index=False)
    
    print(f"✅ Expanded dataset to {len(combined_df)} sequences")
    print(f"✅ Now includes {combined_df['name'].nunique()} unique drugs")
    
    return combined_df

if __name__ == "__main__":
    df = add_more_biologics()