/**
 * scripts/test_rag.ts
 * Test the complete RAG pipeline locally
 * 
 * Run: npx tsx scripts/test_rag.ts
 */
import "dotenv/config";
import { embedText, generateAnswer, checkGeminiConnection } from '../lib/gemini';
import { findSimilarChunks, debugSimilarityScores } from '../lib/retriever';
import { buildPrompt } from '../lib/prompt';


console.log("KEY:", !!process.env.GEMINI_API_KEY, !!process.env.GOOGLE_API_KEY);

console.log("ENV CHECK:", {
  cwd: process.cwd(),
  geminiKey: process.env.GEMINI_API_KEY,
  geminiKeyLen: process.env.GEMINI_API_KEY?.length,
});


// Test questions (realistic policy queries)
const TEST_QUESTIONS = [
  "What are the key benefits of this health insurance policy?",
  "Is pre-existing disease covered?",
  "What is the waiting period for maternity benefits?",
  "What are the exclusions under this policy?",
  "Does this policy cover day care procedures?",
  "What is the Unlimited Reset Benefit?",
  "Are dental expenses covered?",
  "What is the eligibility age for this policy?"
];

/**
 * Test single question through RAG pipeline
 */
async function testQuestion(question: string, verbose: boolean = false): Promise<void> {
  console.log('\n' + '='.repeat(80));
  console.log(`📝 Question: ${question}`);
  console.log('='.repeat(80));
  
  try {
    // Step 1: Embed the question
    console.log('\n⏳ Step 1: Embedding query...');
    const queryEmbedding = await embedText(question);
    console.log(`✅ Embedding generated (${queryEmbedding.length} dimensions)`);
    
    // Step 2: Retrieve similar chunks
    console.log('\n⏳ Step 2: Finding similar chunks...');
    const topK = 3;
    const chunks = findSimilarChunks(queryEmbedding, topK);
    console.log(`✅ Retrieved ${chunks.length} chunks`);
    
    if (verbose) {
      chunks.forEach((chunk, i) => {
        console.log(`\n   ${i + 1}. [${chunk.section}] - Similarity: ${chunk.similarity.toFixed(4)}`);
        console.log(`      Preview: ${chunk.text.substring(0, 150)}...`);
      });
    }
    
    // Step 3: Build prompt
    console.log('\n⏳ Step 3: Building prompt...');
    const prompt = buildPrompt(question, chunks);
    console.log(`✅ Prompt ready (${prompt.length} characters)`);
    
    // Step 4: Generate answer
    console.log('\n⏳ Step 4: Generating answer...');
    const answer = await generateAnswer(prompt);
    console.log(`✅ Answer generated\n`);
    
    // Display answer
    console.log('📄 ANSWER:');
    console.log('-'.repeat(80));
    console.log(answer);
    console.log('-'.repeat(80));
    
    // Show sources
    console.log('\n📚 SOURCES:');
    chunks.forEach((chunk, i) => {
      console.log(`   ${i + 1}. Section: ${chunk.section} (${(chunk.similarity * 100).toFixed(1)}% relevant)`);
    });
    
  } catch (error) {
    console.error('\n❌ Error:', error);
  }
}

/**
 * Run all test questions
 */
async function runAllTests(): Promise<void> {
  console.log('\n🚀 Starting RAG Pipeline Tests\n');
  
  // Check API connection first
  console.log('🔌 Checking Gemini API connection...');
  const connected = await checkGeminiConnection();
  
  if (!connected) {
    console.error('❌ Gemini API connection failed!');
    console.error('   Check your GEMINI_API_KEY in .env file');
    process.exit(1);
  }
  console.log('✅ Gemini API connected\n');
  
  // Run each test
  for (let i = 0; i < TEST_QUESTIONS.length; i++) {
    await testQuestion(TEST_QUESTIONS[i], false);
    
    // Pause between questions to avoid rate limits
    if (i < TEST_QUESTIONS.length - 1) {
      console.log('\n⏸️  Pausing 2 seconds...\n');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  console.log('\n✅ All tests completed!\n');
}

/**
 * Interactive mode: test custom question
 */
async function interactiveTest(): Promise<void> {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  console.log('\n🤖 Interactive RAG Testing Mode');
  console.log('Type your question (or "quit" to exit)\n');
  
  const askQuestion = () => {
    rl.question('Your question: ', async (question: string) => {
      if (question.toLowerCase() === 'quit') {
        console.log('\n👋 Goodbye!\n');
        rl.close();
        return;
      }
      
      if (question.trim()) {
        await testQuestion(question, true);
      }
      
      askQuestion();
    });
  };
  
  askQuestion();
}

// Main execution
const args = process.argv.slice(2);

if (args.includes('--interactive') || args.includes('-i')) {
  interactiveTest();
} else if (args.includes('--question') || args.includes('-q')) {
  const questionIndex = args.indexOf('--question') || args.indexOf('-q');
  const question = args[questionIndex + 1];
  if (question) {
    testQuestion(question, true);
  } else {
    console.error('❌ Please provide a question after --question flag');
  }
} else {
  runAllTests();
}