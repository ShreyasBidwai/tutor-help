"""Script to build FAISS index from help bot Q&A pairs"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.rag_system import get_rag_system

def main():
    print("=" * 50)
    print("Building RAG Index for Niya Help Bot")
    print("=" * 50)
    
    # Load Q&A pairs from JSON file
    qa_file = 'data/niya_qa_pairs.json'
    print(f"\n1. Loading Q&A pairs from {qa_file}...")
    
    if not os.path.exists(qa_file):
        print(f"ERROR: {qa_file} not found!")
        print("Please create the Q&A pairs JSON file first.")
        return
    
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
    
    print(f"   Loaded {len(qa_pairs)} Q&A pairs")
    
    # Initialize RAG system
    print("\n2. Initializing RAG system...")
    rag = get_rag_system()
    
    # Build FAISS index
    print("\n3. Building FAISS index with TF-IDF...")
    print("   This will be very fast (1-2 seconds)...")
    rag.build_faiss_index(qa_pairs, force_rebuild=True)
    
    print("\n" + "=" * 50)
    print("✅ RAG Index built successfully!")
    print("=" * 50)
    print(f"\nTotal Q&A pairs: {len(qa_pairs)}")
    print(f"Index saved to: {rag.faiss_index_path}")
    print(f"Q&A data saved to: {rag.qa_data_path}")
    print(f"\nSimilarity threshold: {rag.similarity_threshold}")
    print("Ready to use RAG system!")

if __name__ == '__main__':
    main()

