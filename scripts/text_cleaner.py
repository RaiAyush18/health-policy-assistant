#!/usr/bin/env python3
"""
Phase 1.3: Text Cleaner
Normalizes extracted text for LLM consumption
Merges broken sentences, standardizes formatting
"""

import re
from pathlib import Path

class TextCleaner:
    def __init__(self):
        self.input_path = Path("data/processed/policy_raw.txt")
        self.output_path = Path("data/processed/policy_clean.txt")
    
    def load_raw_text(self) -> str:
        """Load the raw extracted text"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Raw text not found: {self.input_path}")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def remove_page_markers(self, text: str) -> str:
        """Remove [PAGE N] markers added during extraction"""
        return re.sub(r'\[PAGE \d+\]', '', text)
    
    def normalize_whitespace(self, text: str) -> str:
        """Fix spacing issues"""
        # Remove extra spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix newlines around bullet points
        text = re.sub(r'\n•\s*', '\n• ', text)
        text = re.sub(r'\n-\s*', '\n- ', text)
        
        # Normalize line breaks (max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def merge_broken_sentences(self, text: str) -> str:
        """Fix sentences split across lines"""
        # Common pattern: line ends without punctuation
        # Next line starts with lowercase
        text = re.sub(r'([a-z,])\n([a-z])', r'\1 \2', text)
        
        # Fix currency symbols split from numbers
        text = re.sub(r'`\s+(\d)', r'₹\1', text)
        
        return text
    
    def standardize_bullets(self, text: str) -> str:
        """Standardize bullet point formats"""
        # Convert various bullet styles to consistent format
        text = re.sub(r'\n[•●○]\s*', '\n• ', text)
        text = re.sub(r'\n-\s+', '\n• ', text)
        
        return text
    
    def clean_premium_tables(self, text: str) -> str:
        """Mark premium table sections clearly"""
        # These tables are important but noisy
        # Mark them for potential filtering during chunking
        
        text = re.sub(
            r'(HEALTH \w+ PLUS - PREMIUM CHART)',
            r'\n### PREMIUM TABLE START ###\n\1',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def enhance_section_markers(self, text: str) -> str:
        """Improve section identification"""
        
        # Mark coverage sections
        patterns = {
            'COVERAGE': r'(The Coverage Entails:|Coverage up to)',
            'WAITING_PERIOD': r'(waiting period|PED waiting period)',
            'EXCLUSIONS': r'(What We Will Not Pay|Exclusions?)',
            'BENEFITS': r'(Unlimited Reset Benefit|ASI Protector)',
            'CLAIMS': r'(How Do I Make A Claim|Claim Service Guarantee)',
        }
        
        for section_type, pattern in patterns.items():
            # Don't modify existing section markers
            text = re.sub(
                f'(?<!### SECTION: )({pattern})',
                r'### TOPIC: ' + section_type + r' ###\n\1',
                text,
                flags=re.IGNORECASE
            )
        
        return text
    
    def save_clean_text(self, text: str):
        """Save cleaned text"""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"💾 Saved clean text to: {self.output_path}")
        
        # Stats
        lines = text.count('\n')
        words = len(text.split())
        print(f"📊 Lines: {lines:,} | Words: {words:,} | Chars: {len(text):,}")
    
    def clean(self):
        """Main cleaning pipeline"""
        print("\n🧹 Starting text cleaning...\n")
        
        # Load
        print("📂 Loading raw text...")
        text = self.load_raw_text()
        print(f"✅ Loaded {len(text):,} characters")
        
        # Clean step by step
        steps = [
            ("Removing page markers", self.remove_page_markers),
            ("Normalizing whitespace", self.normalize_whitespace),
            ("Merging broken sentences", self.merge_broken_sentences),
            ("Standardizing bullets", self.standardize_bullets),
            ("Cleaning premium tables", self.clean_premium_tables),
            ("Enhancing section markers", self.enhance_section_markers),
        ]
        
        for step_name, step_func in steps:
            print(f"⚙️  {step_name}...")
            text = step_func(text)
        
        # Save
        self.save_clean_text(text)
        
        print("\n✅ Phase 1.3 complete!")
        print("➡️  Next: Run python scripts/chunker.py")

def main():
    cleaner = TextCleaner()
    cleaner.clean()

if __name__ == "__main__":
    main()