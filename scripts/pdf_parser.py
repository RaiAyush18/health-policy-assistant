#!/usr/bin/env python3
"""
Phase 1.2: PDF Parser
Extracts clean text from ICICI Lombard Health Policy PDF
Preserves structure, removes noise
"""

import re
from pathlib import Path
from pypdf import PdfReader

class PolicyPDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.output_path = Path("data/processed/policy_raw.txt")
        
    def extract_text(self) -> str:
        """Extract all text from PDF page by page"""
        print(f"📄 Reading PDF: {self.pdf_path}")
        
        try:
            reader = PdfReader(str(self.pdf_path))
            total_pages = len(reader.pages)
            print(f"📊 Total pages: {total_pages}")
            
            all_text = []
            
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                
                # Add page marker for debugging (will be removed later)
                all_text.append(f"\n[PAGE {i}]\n{text}")
                
                if i % 10 == 0:
                    print(f"⏳ Processed {i}/{total_pages} pages...")
            
            print(f"✅ Extracted text from all {total_pages} pages")
            return "\n".join(all_text)
            
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            raise
    
    def clean_headers_footers(self, text: str) -> str:
        """Remove repeated headers, footers, page numbers"""
        
        # Remove common footer patterns
        text = re.sub(r'ICICI\s+LOMBARD.*?(?=\n)', '', text, flags=re.IGNORECASE)
        
        # Remove standalone page numbers
        text = re.sub(r'\n\d+\n', '\n', text)
        
        # Remove "Rates are exclusive of GST" repeated lines
        text = re.sub(r'Rates are (?:in|ex)clusive of GST.*?\n', '', text, flags=re.IGNORECASE)
        
        # Remove multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def preserve_structure(self, text: str) -> str:
        """Mark important sections clearly"""
        
        # Identify major sections and mark them
        section_patterns = [
            (r'\n(Key Points To Note:)', r'\n\n### SECTION: KEY POINTS ###\n\1'),
            (r'\n(Major Permanent Exclusions)', r'\n\n### SECTION: EXCLUSIONS ###\n\1'),
            (r'\n(How Do I Make A Claim\?)', r'\n\n### SECTION: CLAIMS PROCESS ###\n\1'),
            (r'\n(Health Insurance FAQs)', r'\n\n### SECTION: FAQs ###\n\1'),
            (r'\n(Plan Name\s+Health \w+)', r'\n\n### SECTION: PLAN DETAILS ###\n\1'),
        ]
        
        for pattern, replacement in section_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def save_raw_text(self, text: str):
        """Save extracted text to file"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"💾 Saved raw text to: {self.output_path}")
        print(f"📏 Total characters: {len(text):,}")
    
    def parse(self):
        """Main parsing pipeline"""
        print("\n🚀 Starting PDF parsing...\n")
        
        # Step 1: Extract
        raw_text = self.extract_text()
        
        # Step 2: Clean
        print("\n🧹 Cleaning headers and footers...")
        cleaned_text = self.clean_headers_footers(raw_text)
        
        # Step 3: Structure
        print("🏗️  Preserving document structure...")
        structured_text = self.preserve_structure(cleaned_text)
        
        # Step 4: Save
        self.save_raw_text(structured_text)
        
        print("\n✅ Phase 1.2 complete!")
        print(f"➡️  Next: Run python scripts/text_cleaner.py")

def main():
    pdf_path = "data/raw/Health-Insurance-policy.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        print("📋 Please place the ICICI policy PDF in data/raw/")
        return
    
    parser = PolicyPDFParser(pdf_path)
    parser.parse()

if __name__ == "__main__":
    main()