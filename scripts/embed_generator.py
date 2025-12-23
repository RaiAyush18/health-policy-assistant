#!/usr/bin/env python3
"""
Phase 1.5: Embedding Generator
Generates semantic embeddings using Gemini
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    def __init__(self, skip_premium_tables=True):
        self.input_path = Path("data/processed/chunks.json")
        self.output_path = Path("data/processed/embeddings.json")
        self.skip_premium_tables = skip_premium_tables
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        self.client = genai.Client(api_key=api_key)
        print("✅ Gemini API configured")
    
    def load_chunks(self) -> List[Dict]:
        """Load chunks from JSON"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Chunks not found: {self.input_path}")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text chunk"""
        try:
            result = self.client.models.embed_content(
                model="models/text-embedding-004",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"⚠️  Error generating embedding: {e}")
            return None
    
    def generate_all_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for all chunks with progress tracking"""
        total = len(chunks)
        embeddings_data = []
        
        print(f"\n🔄 Generating embeddings for {total} chunks...")
        print("⏱️  This may take a few minutes...\n")
        
        for i, chunk in enumerate(chunks, 1):
            # Skip premium tables if desired
            if self.skip_premium_tables and chunk.get('is_premium_table', False):
                print(f"⏭️  Skipping premium table chunk {i}/{total}")
                continue
            
            # Generate embedding
            embedding = self.generate_embedding(chunk['text'])
            
            if embedding:
                embeddings_data.append({
                    'chunk_id': chunk['chunk_id'],
                    'section': chunk['section'],
                    'text': chunk['text'],
                    'token_count': chunk['token_count'],
                    'embedding': embedding,
                    'embedding_dim': len(embedding),
                    'is_premium_table': chunk.get('is_premium_table', False),
                    'priority': 'low' if chunk.get('is_premium_table') else 'high'
                })
                
                # Progress indicator
                if i % 10 == 0:
                    print(f"✅ Progress: {i}/{total} chunks")
            else:
                print(f"❌ Failed to embed chunk {chunk['chunk_id']}")
            
            # Rate limiting
            time.sleep(0.5)
        
        return embeddings_data
    
    def save_embeddings(self, embeddings: List[Dict]):
        """Save embeddings to JSON file"""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(embeddings)} embeddings to: {self.output_path}")
        
        # Create metadata file
        metadata_path = Path("data/processed/chunks_metadata.json")
        metadata = [
            {
                'chunk_id': e['chunk_id'],
                'section': e['section'],
                'text_preview': e['text'][:200] + "...",
                'token_count': e['token_count'],
                'embedding_dim': e['embedding_dim']
            }
            for e in embeddings
        ]
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Saved metadata to: {metadata_path}")
        
        # Stats
        print(f"\n📊 Embedding Statistics:")
        print(f"   Total embeddings: {len(embeddings)}")
        print(f"   Embedding dimension: {embeddings[0]['embedding_dim']}")
        print(f"   Total tokens: {sum(e['token_count'] for e in embeddings):,}")
        
        file_size = self.output_path.stat().st_size / (1024 * 1024)
        print(f"   File size: {file_size:.2f} MB")
    
    def generate(self):
        """Main embedding generation pipeline"""
        print("\n🧠 Starting embedding generation...\n")
        
        # Load chunks
        print("📂 Loading chunks...")
        chunks = self.load_chunks()
        print(f"✅ Loaded {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = self.generate_all_embeddings(chunks)
        
        # Save
        self.save_embeddings(embeddings)
        
        print("\n✅ Phase 1.5 complete!")
        print("\n🎉 PHASE 1 FINISHED!")

def main():
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found!")
        print("\n📋 Setup instructions:")
        print("1. Create a .env file in project root")
        print("2. Add: GEMINI_API_KEY=your_key_here")
        print("3. Get your key from: https://aistudio.google.com/app/apikey")
        return
    
    generator = EmbeddingGenerator()
    generator.generate()

if __name__ == "__main__":
    main()