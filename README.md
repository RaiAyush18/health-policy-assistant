# 🏥 Health Insurance Policy Intelligence Assistant

**A RAG-based system for accurate interpretation of health insurance policy documents**

---

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Why This Exists](#why-this-exists)
- [What This System Does](#what-this-system-does)
- [What This System Does NOT Do](#what-this-system-does-not-do)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

---

## 🎯 Problem Statement

Health insurance policies are:
- **Long** (40-120 pages on average)
- **Clause-heavy** with complex legal language
- **Easy to misinterpret** even by trained staff
- **Risky if misunderstood** — wrong guidance can lead to claim denials

Insurance operations teams, agents, and underwriting staff need a reliable way to:
- Quickly interpret policy clauses
- Answer eligibility and coverage questions accurately
- Identify applicable waiting periods and exclusions
- **Provide source-backed answers** to minimize errors

This project addresses that gap using Retrieval-Augmented Generation (RAG).

---

## 💡 Why This Exists

**Traditional approaches fail because:**
- ❌ Generic chatbots hallucinate or provide vague answers
- ❌ PDF summarizers miss nuanced clause interpretations
- ❌ Keyword search doesn't understand context or intent

**This system is different because:**
- ✅ Grounds every answer in actual policy text
- ✅ Cites clause numbers and page references
- ✅ Designed for **decision-support**, not just information retrieval
- ✅ Built with enterprise-grade answer discipline

---

## ✅ What This System Does

This assistant helps users answer **interpretive and conditional queries** such as:

### 🔹 Interpretive Questions
- *"Is knee replacement covered if done within 18 months of policy start?"*
- *"Does this policy cover pre-existing diabetes complications?"*
- *"What happens if hospitalization is less than 24 hours?"*

### 🔹 Conditional Queries
- *"If the policyholder is 45 years old with hypertension, what clauses apply?"*
- *"What changes if this is a renewal policy vs first-time purchase?"*

### 🔹 Policy Comparisons (within same document)
- *"Difference between room rent limit and ICU charges"*
- *"Day-care procedures vs OPD coverage"*

### 🔹 Source-Grounded Answers
Every response includes:
> *"According to Clause 5.2 (Page 18)..."*

---

## ❌ What This System Does NOT Do

To maintain focus and quality, this system intentionally does NOT:

- ❌ Handle multiple insurance policies simultaneously
- ❌ Compare policies across different insurers
- ❌ Process user-uploaded documents (single policy only)
- ❌ File claims or perform transactions
- ❌ Provide personalized insurance recommendations
- ❌ Replace professional insurance advice

**This is a depth-first learning project, not a breadth-first production tool.**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS |
| **AI/LLM** | Google Gemini API |
| **RAG Framework** | LangChain (minimal usage) |
| **Vector Store** | Supabase pgvector / Pinecone *(planned)* |
| **Deployment** | Vercel |

---

## 📁 Project Structure

```
Health-policy-assistant/
│
├── app/
│   ├── page.tsx              # Main UI
│   ├── layout.tsx            # App layout
│   └── api/
│       └── chat/
│           └── route.ts      # API endpoint for queries
│
├── lib/
│   ├── gemini.ts             # Gemini API integration
│   ├── retriever.ts          # Vector retrieval logic
│   ├── prompt.ts             # Prompt templates
│   └── types.ts              # TypeScript types
│
├── scripts/
│   ├── pdf_parser.py         # Extract text from policy PDF
│   ├── chunker.py            # Clause-aware chunking
│   └── embed_upload.py       # Generate & store embeddings
│
├── data/
│   ├── raw/                  # Original policy PDF
│   └── processed/            # Chunked text + metadata
│
├── public/
│   └── disclaimer.txt        # Legal disclaimer
│
├── README.md
├── .gitignore
├── package.json
└── tsconfig.json
```

---

## 🔄 How It Works

### **Phase 1: Data Ingestion (Offline)**
```
Policy PDF → Text Extraction → Clause-Aware Chunking → Embedding Generation → Vector Store
```

### **Phase 2: Query Processing (Runtime)**
```
User Question → Query Embedding → Similarity Search → Retrieve Top Chunks → Prompt Assembly → Gemini Response
```

### **Key Design Principles:**
1. **Clause-aware chunking** (not blind 1000-token splits)
2. **Strict source grounding** (no hallucinated answers)
3. **Metadata preservation** (section names, clause numbers, page refs)
4. **Controlled prompt engineering** (context-only responses)

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+ (for data processing scripts)
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/health-policy-assistant.git
cd health-policy-assistant

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Add your GEMINI_API_KEY

# Run development server
npm run dev
```

Visit `http://localhost:3000`

### Data Preparation

```bash
# 1. Place policy PDF in data/raw/
# 2. Run processing scripts
python scripts/pdf_parser.py
python scripts/chunker.py
python scripts/embed_upload.py
```

---

## 🗺️ Roadmap

- [x] Project scoping and architecture design
- [ ] PDF parsing and clause extraction
- [ ] Clause-aware chunking implementation
- [ ] Vector embeddings and storage setup
- [ ] Next.js UI development
- [ ] Gemini API integration
- [ ] Retrieval logic and prompt engineering
- [ ] Testing with 20+ realistic queries
- [ ] Deployment to Vercel
- [ ] Documentation and case studies

---

## ⚠️ Disclaimer

This is a **learning project** and a technical demonstration.

- **NOT for production use** in making actual insurance decisions
- **NOT a substitute** for professional insurance advice
- **NOT affiliated** with any insurance company
- Built using publicly available policy documents for educational purposes

Always consult licensed insurance professionals for policy-related decisions.

---

## 📧 Contact

**Project by:** [Ayush Rai]  
**LinkedIn:** [[Your Profile](https://www.linkedin.com/in/ayush-rai-22b38b257/)]  
**Email:** [ayushalokrai@gmail.com]



