/**
 * lib/gemini.ts
 * Pure Gemini API interface
 * Responsibilities:
 * 1. Embed text into vectors
 * 2. Generate answers from prompts
 * 
 * NO business logic here. Just API calls.
 */

import { GoogleGenAI } from '@google/genai';

// Initialize Gemini client
const genAI = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY!,
});

/**
 * Embed a text query into a vector
 * Uses same model as Phase 1 (CRITICAL)
 */
export async function embedText(text: string): Promise<number[]> {
  try {
    const result = await genAI.models.embedContent({
      model: "text-embedding-004",
      contents: [{ role: "user", parts: [{ text }] }],
    });
    
    const embedding = result.embeddings?.[0]?.values;
    
    if (!embedding || embedding.length === 0) {
      throw new Error("Empty embedding returned");
    }
    
    return embedding;
  } catch (error) {
    console.error("Embedding error:", error);
    throw new Error(`Failed to embed text: ${error}`);
  }
}

/**
 * Generate answer from prompt using Gemini
 * Temperature is LOW for factual answers
 */
export async function generateAnswer(prompt: string): Promise<string> {
  try {
    const result = await genAI.models.generateContent({
      model: "gemini-2.5-flash",  // ✅ Changed from "gemini-1.5-pro-latest"
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      config: {
        temperature: 0.1,
        
      },
    });
    
    const text = result.text;
    
    if (!text) {
      throw new Error("Empty response from Gemini");
    }
    
    return text;
  } catch (error) {
    console.error("Generation error:", error);
    throw new Error(`Failed to generate answer: ${error}`);
  }
}

/**
 * Health check: verify API key works
 */
export async function checkGeminiConnection(): Promise<boolean> {
  try {
    await embedText('test');
    return true;
  } catch {
    return false;
  }
}