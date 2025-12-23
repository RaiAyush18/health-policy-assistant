#!/usr/bin/env python3
"""
Master Script: Run Complete Phase 1 Pipeline
Executes all Phase 1 scripts in order
"""

import subprocess
import sys
from pathlib import Path

def run_command(command: str, description: str):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("\n🔍 Checking prerequisites...\n")
    
    checks = {
        "PDF exists": Path("data/raw/Health-Insurance-policy.pdf").exists(),
        ".env exists": Path(".env").exists(),
        "requirements.txt": Path("requirements.txt").exists(),
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
    
    if not all_good:
        print("\n⚠️  Prerequisites not met!")
        print("\n📋 Setup checklist:")
        print("1. Place policy PDF in: data/raw/Health-Insurance-policy.pdf")
        print("2. Create .env file with: GEMINI_API_KEY=your_key")
        print("3. Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All prerequisites met!\n")
    return True

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║    ICICI Health Policy Intelligence Assistant             ║
║    Phase 1: Data Ingestion Pipeline                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Define pipeline steps
    steps = [
        ("python scripts/pdf_parser.py", "Step 1/4: PDF Parsing"),
        ("python scripts/text_cleaner.py", "Step 2/4: Text Cleaning"),
        ("python scripts/chunker.py", "Step 3/4: Clause-Aware Chunking"),
        ("python scripts/embed_generator.py", "Step 4/4: Embedding Generation"),
    ]
    
    # Run pipeline
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n💥 Pipeline failed at: {description}")
            sys.exit(1)
    
    # Success summary
    print(f"\n{'='*60}")
    print("🎉 PHASE 1 COMPLETE!")
    print(f"{'='*60}\n")
    
    print("📊 Generated Files:")
    files = [
        "data/processed/policy_raw.txt",
        "data/processed/policy_clean.txt",
        "data/processed/chunks.json",
        "data/processed/embeddings.json",
        "data/processed/chunks_metadata.json"
    ]
    
    for file_path in files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size / 1024
            print(f"   ✅ {file_path} ({size:.1f} KB)")
    
    print("\n📋 What you have now:")
    print("   • Clean, structured policy text")
    print("   • Semantically meaningful chunks")
    print("   • Vector embeddings for retrieval")
    print("   • Metadata for source attribution")
    
    print("\n➡️  Next Steps:")
    print("   1. Review chunks in: data/processed/chunks_metadata.json")
    print("   2. Test retrieval quality manually")
    print("   3. Move to Phase 2: Build query system")
    
    print("\n💡 Quick Test:")
    print("   python -c 'import json; print(len(json.load(open(\"data/processed/chunks.json\"))))'")

if __name__ == "__main__":
    main()