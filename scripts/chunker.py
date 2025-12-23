#!/usr/bin/env python3
"""
Phase 1.4: Clause-Aware Chunker
Creates semantically meaningful chunks with metadata
This is the MOST IMPORTANT phase for RAG quality
"""

import json
import re
from pathlib import Path
from typing import List, Dict
import tiktoken

class ClauseAwareChunker:
    def __init__(self, target_size: int = 600, overlap: int = 100):
        self.input_path = Path("data/processed/policy_clean.txt")
        self.output_path = Path("data/processed/chunks.json")
        self.target_size = target_size  # tokens
        self.overlap = overlap  # tokens
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def load_clean_text(self) -> str:
        """Load cleaned text"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Clean text not found: {self.input_path}")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def split_into_sections(self, text: str) -> List[Dict]:
        """Split by major sections first"""
        sections = []
        
        # Split by section markers
        parts = re.split(r'(### SECTION: [^#]+###)', text)
        
        current_section = "Introduction"
        current_text = ""
        
        for part in parts:
            if part.startswith("### SECTION:"):
                # Save previous section
                if current_text.strip():
                    sections.append({
                        'section': current_section,
                        'text': current_text.strip()
                    })
                
                # Extract new section name
                current_section = re.search(r'### SECTION: (.+?) ###', part).group(1)
                current_text = ""
            else:
                current_text += part
        
        # Add last section
        if current_text.strip():
            sections.append({
                'section': current_section,
                'text': current_text.strip()
            })
        
        return sections
    
    def identify_clauses(self, text: str) -> List[str]:
        """Split text by clauses/subsections"""
        # Split on:
        # - Bullet points
        # - Numbered items
        # - Natural paragraph breaks
        
        clauses = []

        # If this looks like a premium table, split differently
        if 'PREMIUM CHART' in text or 'PREMIUM TABLE' in text:
            # Split by age ranges or plan types
            parts = re.split(r'\n(?=Age / SI|Indiv\.|2A\n)', text)
            return [p.strip() for p in parts if p.strip()]
        
        # First split by bullet points or numbers
        parts = re.split(r'\n(?=•|\d+\.)', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # If still too long, split by sentences
            if self.count_tokens(part) > self.target_size:
                sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', part)
                clauses.extend(sentences)
            else:
                clauses.append(part)
        
        return clauses
    
    def create_chunks(self, sections: List[Dict]) -> List[Dict]:
        """Create chunks with metadata"""
        chunks = []
        chunk_id = 0
        
        for section_data in sections:
            section_name = section_data['section']
            section_text = section_data['text']
            
            # Identify clauses in this section
            clauses = self.identify_clauses(section_text)
            
            # Group clauses into target-sized chunks
            current_chunk = []
            current_tokens = 0
            
            for i, clause in enumerate(clauses):
                clause_tokens = self.count_tokens(clause)
                
                # If adding this clause exceeds target, save current chunk
                if current_tokens + clause_tokens > self.target_size and current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    
                    chunks.append({
                        'chunk_id': f"chunk_{chunk_id:04d}",
                        'section': section_name,
                        'text': chunk_text,
                        'token_count': self.count_tokens(chunk_text),
                        'clause_index': f"{i-len(current_chunk)}-{i-1}"
                    })
                    
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    # Keep last clause for context
                    if self.overlap > 0 and len(current_chunk) > 0:
                        current_chunk = [current_chunk[-1], clause]
                        current_tokens = self.count_tokens('\n'.join(current_chunk))
                    else:
                        current_chunk = [clause]
                        current_tokens = clause_tokens
                else:
                    current_chunk.append(clause)
                    current_tokens += clause_tokens
            
            # Save last chunk of section
            if current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'chunk_id': f"chunk_{chunk_id:04d}",
                    'section': section_name,
                    'text': chunk_text,
                    'token_count': self.count_tokens(chunk_text),
                    'clause_index': f"{len(clauses)-len(current_chunk)}-{len(clauses)-1}"
                })
                chunk_id += 1
        
        return chunks
    
    def filter_premium_tables(self, chunks: List[Dict]) -> List[Dict]:
        """Optionally filter out premium table chunks"""
        # Premium tables are noisy and rarely needed for Q&A
        # Keep them but mark them
        
        for chunk in chunks:
            if 'PREMIUM TABLE' in chunk['text'] or 'PREMIUM CHART' in chunk['text']:
                chunk['is_premium_table'] = True
            else:
                chunk['is_premium_table'] = False
        
        return chunks
    
    def save_chunks(self, chunks: List[Dict]):
        """Save chunks to JSON"""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(chunks)} chunks to: {self.output_path}")
        
        # Stats
        total_tokens = sum(c['token_count'] for c in chunks)
        avg_tokens = total_tokens / len(chunks)
        
        print(f"\n📊 Chunk Statistics:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total tokens: {total_tokens:,}")
        print(f"   Average tokens/chunk: {avg_tokens:.0f}")
        print(f"   Target size: {self.target_size} tokens")
        
        # Section breakdown
        sections = {}
        for chunk in chunks:
            section = chunk['section']
            sections[section] = sections.get(section, 0) + 1
        
        print(f"\n📑 Chunks by section:")
        for section, count in sorted(sections.items()):
            print(f"   {section}: {count} chunks")
    
    def chunk(self):
        """Main chunking pipeline"""
        print("\n✂️  Starting clause-aware chunking...\n")
        
        # Load
        print("📂 Loading clean text...")
        text = self.load_clean_text()
        print(f"✅ Loaded {len(text):,} characters")
        
        # Split into sections
        print("\n🔍 Identifying sections...")
        sections = self.split_into_sections(text)
        print(f"✅ Found {len(sections)} major sections")
        
        # Create chunks
        print(f"\n✂️  Creating chunks (target: {self.target_size} tokens, overlap: {self.overlap})...")
        chunks = self.create_chunks(sections)
        
        # Filter/mark premium tables
        print("🏷️  Marking premium table chunks...")
        chunks = self.filter_premium_tables(chunks)
        
        # Save
        self.save_chunks(chunks)
        
        print("\n✅ Phase 1.4 complete!")
        print("➡️  Next: Run python scripts/embed_generator.py")

def main():
    # You can adjust these parameters
    chunker = ClauseAwareChunker(
        target_size=600,  # tokens per chunk
        overlap=100       # overlap tokens
    )
    chunker.chunk()

if __name__ == "__main__":
    main()