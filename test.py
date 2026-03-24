# test_setup.py
print("🧬 Testing BioInsights AI Setup...")

# Test core imports
try:
    import torch
    print("✅ PyTorch installed")
    
    import esm
    print("✅ ESM2 installed")
    
    import faiss
    print("✅ FAISS installed")
    
    import streamlit as st
    print("✅ Streamlit installed")
    
    import plotly.express as px
    print("✅ Plotly installed")
    
    from Bio import SeqIO
    print("✅ Biopython installed")
    
    print("\n🎉 All libraries installed successfully!")
    print("🚀 Ready to build BioInsights AI!")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Run: pip install <missing-library>")