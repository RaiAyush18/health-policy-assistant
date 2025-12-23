/**
 * lib/retriever.ts
 * Pure retrieval logic - NO LLM calls
 * Responsibilities:
 * 1. Load embeddings from JSON
 * 2. Compute cosine similarity
 * 3. Return top-K chunks
 */

import fs from 'fs';
import path from 'path';

export interface Chunk {
  chunk_id: string;
  section: string;
  text: string;
  token_count: number;
  embedding: number[];
  embedding_dim: number;
  is_premium_table?: boolean;
}

export interface RetrievedChunk {
  chunk_id: string;
  section: string;
  text: string;
  similarity: number;
}

/**
 * Load embeddings from Phase 1 output
 */
export function loadEmbeddings(): Chunk[] {
  const embeddingsPath = path.join(process.cwd(), 'data', 'processed', 'embeddings.json');
  
  if (!fs.existsSync(embeddingsPath)) {
    throw new Error(`Embeddings file not found: ${embeddingsPath}`);
  }
  
  const data = fs.readFileSync(embeddingsPath, 'utf-8');
  return JSON.parse(data);
}

/**
 * Compute cosine similarity between two vectors
 * Returns value between -1 (opposite) and 1 (identical)
 */
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  if (vecA.length !== vecB.length) {
    throw new Error('Vector dimensions must match');
  }
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }
  
  normA = Math.sqrt(normA);
  normB = Math.sqrt(normB);
  
  if (normA === 0 || normB === 0) {
    return 0;
  }
  
  return dotProduct / (normA * normB);
}

/**
 * Find top-K most similar chunks to query
 * 
 * @param queryEmbedding - Vector representation of user question
 * @param topK - Number of chunks to return (default: 3)
 * @param filterPremiumTables - Skip premium table chunks (default: true)
 */
export function findSimilarChunks(
  queryEmbedding: number[],
  topK: number = 3,
  filterPremiumTables: boolean = true
): RetrievedChunk[] {
  
  // Load all chunks
  let chunks = loadEmbeddings();
  
  // Filter out premium tables if requested
  if (filterPremiumTables) {
    chunks = chunks.filter(chunk => !chunk.is_premium_table);
  }
  
  // Compute similarity for each chunk
  const similarities = chunks.map(chunk => ({
    chunk_id: chunk.chunk_id,
    section: chunk.section,
    text: chunk.text,
    similarity: cosineSimilarity(queryEmbedding, chunk.embedding)
  }));
  
  // Sort by similarity (highest first)
  similarities.sort((a, b) => b.similarity - a.similarity);
  
  // Return top K
  return similarities.slice(0, topK);
}

/**
 * Debug: Show similarity scores for inspection
 */
export function debugSimilarityScores(
  queryEmbedding: number[],
  topK: number = 5
): void {
  const results = findSimilarChunks(queryEmbedding, topK);
  
  console.log('\n🔍 Top Retrieved Chunks:\n');
  results.forEach((chunk, i) => {
    console.log(`${i + 1}. [${chunk.chunk_id}] ${chunk.section}`);
    console.log(`   Similarity: ${chunk.similarity.toFixed(4)}`);
    console.log(`   Text: ${chunk.text.substring(0, 100)}...`);
    console.log('');
  });
}