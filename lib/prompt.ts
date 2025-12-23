/**
 * lib/prompt.ts
 * Prompt construction logic
 * 
 * THIS FILE IS MORE IMPORTANT THAN THE MODEL.
 * 
 * Responsibilities:
 * 1. Build grounded prompts from chunks
 * 2. Enforce insurance-safe language
 * 3. Prevent hallucination
 */

import { RetrievedChunk } from './retriever';

/**
 * Build the system prompt with strict instructions
 */
function getSystemPrompt(): string {
  return `You are an ICICI Lombard Complete Health Insurance policy assistant.

CRITICAL RULES:
1. Answer ONLY using information from the provided policy context below
2. If the answer is not in the context, say "This information is not available in the policy document"
3. NEVER make assumptions or provide general insurance advice
4. NEVER provide medical or legal advice
5. Always cite the section name when answering
6. Use clear, simple language
7. If waiting periods or exclusions apply, state them clearly

Your goal is to help users understand their policy accurately, not to sell or make claims.`;
}

/**
 * Format retrieved chunks into context
 */
function formatContext(chunks: RetrievedChunk[]): string {
  if (chunks.length === 0) {
    return 'No relevant policy information found.';
  }
  
  let context = 'POLICY CONTEXT:\n\n';
  
  chunks.forEach((chunk, index) => {
    context += `--- Section: ${chunk.section} (Relevance: ${(chunk.similarity * 100).toFixed(1)}%) ---\n`;
    context += chunk.text;
    context += '\n\n';
  });
  
  return context;
}

/**
 * Build complete prompt for Gemini
 * 
 * @param userQuestion - Original user query
 * @param retrievedChunks - Top-K relevant chunks
 */
export function buildPrompt(
  userQuestion: string,
  retrievedChunks: RetrievedChunk[]
): string {
  const systemPrompt = getSystemPrompt();
  const context = formatContext(retrievedChunks);
  
  return `${systemPrompt}

${context}

USER QUESTION: ${userQuestion}

ANSWER (Remember: Only use information from the context above):`;
}

/**
 * Alternative: Stricter prompt for edge cases
 * Use this if you detect hallucination
 */
export function buildStrictPrompt(
  userQuestion: string,
  retrievedChunks: RetrievedChunk[]
): string {
  const context = formatContext(retrievedChunks);
  
  return `You are analyzing an ICICI Lombard health insurance policy document.

${context}

Question: ${userQuestion}

Instructions:
1. Read the policy context carefully
2. Find the exact information that answers the question
3. If the answer exists in the context:
   - State the answer clearly
   - Mention which section it comes from
   - Include any conditions or limitations mentioned
4. If the answer does NOT exist in the context:
   - Say exactly: "This specific information is not covered in the provided policy sections"
   - Do NOT guess or provide general insurance knowledge

Answer:`;
}

/**
 * Build prompt for yes/no questions
 * Useful for coverage checks
 */
export function buildCoverageCheckPrompt(
  userQuestion: string,
  retrievedChunks: RetrievedChunk[]
): string {
  const context = formatContext(retrievedChunks);
  
  return `You are checking ICICI Lombard Complete Health Insurance policy coverage.

${context}

Question: ${userQuestion}

Provide a clear YES or NO answer, followed by:
- The relevant policy section
- Any waiting periods that apply
- Any conditions or exclusions
- The specific clause/benefit name

Format:
Answer: [YES/NO]
Source: [Section name]
Details: [Explanation with conditions]

Your response:`;
}