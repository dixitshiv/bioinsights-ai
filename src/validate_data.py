# src/validate_data.py
import pandas as pd
import re

def validate_protein_sequences(df):
    """Validate that our protein sequences are properly formatted"""
    
    print("🔍 Validating protein sequences...")
    
    # Check for valid amino acid sequences
    valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
    errors = []
    
    for idx, row in df.iterrows():
        sequence = row['sequence']
        
        # Check length
        if len(sequence) < 50:
            errors.append(f"Row {idx}: Sequence too short ({len(sequence)} aa)")
            
        # Check for invalid characters
        invalid_chars = set(sequence) - valid_aa
        if invalid_chars:
            errors.append(f"Row {idx}: Invalid amino acids: {invalid_chars}")
            
        # Check if sequence is all uppercase
        if sequence != sequence.upper():
            errors.append(f"Row {idx}: Sequence not uppercase")
    
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ All sequences valid!")
        print(f"✅ {len(df)} sequences passed validation")
        
    return len(errors) == 0

def main():
    df = pd.read_csv("data/drugbank_biologics.csv")
    is_valid = validate_protein_sequences(df)
    
    if is_valid:
        print("\n🎉 Dataset ready for ESM2 processing!")
    else:
        print("\n⚠️  Please fix validation errors before proceeding")

if __name__ == "__main__":
    main()