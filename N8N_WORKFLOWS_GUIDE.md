# 🎯 n8n Workflows Guide - AWS Certifications Coach

Complete guide to build all n8n workflows for your learning platform.

## 📋 Table of Contents

1. [AI Study Coach (Chat)](#1-ai-study-coach-chat)
2. [Practice Exam Generator](#2-practice-exam-generator)
3. [Study Tricks & Mnemonics](#3-study-tricks--mnemonics)
4. [Answer Evaluation](#4-answer-evaluation)
5. [Q&A Knowledge Base](#5-qa-knowledge-base)
---

## 1. AI Study Coach (Chat)

### 🎯 Purpose
Context-aware AI conversations with Redis chat memory for personalized learning.

### 📊 Workflow Architecture

```
Webhook Trigger → Load Chat History (Redis) → Build Context → LLM Call → Save to Redis → Save to Snowflake → Return Response
```

### 🔧 n8n Nodes Setup

#### Node 1: Webhook Trigger
- **Type:** Webhook
- **Method:** POST
- **Path:** `/chat`
- **Response Mode:** Last Node
- **Expected Input:**
```json
{
  "user_id": 123,
  "question": "What is S3?",
  "context": "AWS Certified Solutions Architect - Associate",
  "timestamp": "2025-12-06T01:00:00Z"
}
```

#### Node 2: Load Chat History (Redis)
- **Type:** Redis
- **Operation:** Get
- **Key:** `chat_history:{{$json.user_id}}`
- **Purpose:** Retrieve last 10 messages for context

**Settings:**
- Host: Your Redis host
- Port: 6379
- Database: 0

#### Node 3: Format Chat Context
- **Type:** Code (JavaScript)
- **Purpose:** Build conversation context for LLM

```javascript
// Get webhook data
const userId = $input.first().json.user_id;
const question = $input.first().json.question;
const certification = $input.first().json.context;

// Get chat history from Redis
const historyData = $input.all()[1].json;
let chatHistory = [];

try {
  if (historyData && historyData.value) {
    chatHistory = JSON.parse(historyData.value);
  }
} catch (e) {
  chatHistory = [];
}

// Build context for LLM
const systemPrompt = `You are an expert AWS certification coach specializing in ${certification}. 
Your role is to:
- Provide accurate, exam-focused answers
- Use real-world examples and scenarios
- Break down complex topics
- Reference AWS documentation
- Help students understand WHY, not just WHAT

Current certification focus: ${certification}`;

// Format messages for LLM
const messages = [
  { role: "system", content: systemPrompt }
];

// Add recent history (last 5 exchanges)
chatHistory.slice(-10).forEach(msg => {
  messages.push(msg);
});

// Add current question
messages.push({ role: "user", content: question });

return {
  user_id: userId,
  question: question,
  certification: certification,
  messages: messages,
  history_length: chatHistory.length
};
```

#### Node 4: Call LLM (Claude/GPT)
- **Type:** HTTP Request or OpenAI/Anthropic Node
- **Purpose:** Generate AI response

**For Claude (Anthropic):**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 2000,
  "temperature": 0.7,
  "messages": "={{$json.messages}}"
}
```

**For GPT (OpenAI):**
```json
{
  "model": "gpt-4-turbo",
  "messages": "={{$json.messages}}",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

#### Node 5: Extract & Format Response
- **Type:** Code (JavaScript)

```javascript
const response = $input.first().json;
let answer = "";

// Extract response based on provider
if (response.content && response.content[0]) {
  // Claude response
  answer = response.content[0].text;
} else if (response.choices && response.choices[0]) {
  // OpenAI response
  answer = response.choices[0].message.content;
}

return {
  user_id: $node["Format Chat Context"].json.user_id,
  question: $node["Format Chat Context"].json.question,
  answer: answer,
  timestamp: new Date().toISOString()
};
```

#### Node 6: Update Redis Chat History
- **Type:** Code (JavaScript) → Redis Set

```javascript
// Get current chat history
const userId = $json.user_id;
const question = $json.question;
const answer = $json.answer;

// Load existing history
let chatHistory = [];
try {
  const historyData = $node["Load Chat History"].json;
  if (historyData && historyData.value) {
    chatHistory = JSON.parse(historyData.value);
  }
} catch (e) {
  chatHistory = [];
}

// Add new exchange
chatHistory.push({ role: "user", content: question });
chatHistory.push({ role: "assistant", content: answer });

// Keep only last 20 messages (10 exchanges)
if (chatHistory.length > 20) {
  chatHistory = chatHistory.slice(-20);
}

return {
  key: `chat_history:${userId}`,
  value: JSON.stringify(chatHistory),
  expire: 86400, // 24 hours
  answer: answer
};
```

**Then connect to:**
- **Redis Node:** Set operation with key/value from above

#### Node 7: Save to Snowflake (Optional)
- **Type:** Postgres/Snowflake
- **Query:**
```sql
INSERT INTO chat_history (user_id, question, answer, timestamp)
VALUES ({{$json.user_id}}, '{{$json.question}}', '{{$json.answer}}', '{{$json.timestamp}}')
```

#### Node 8: Return Response
- **Type:** Respond to Webhook
- **Response:**
```json
{
  "answer": "={{$json.answer}}",
  "timestamp": "={{$json.timestamp}}",
  "status": "success"
}
```

### 🔑 Environment Variables Needed
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- `REDIS_HOST`
- `REDIS_PORT`
- `SNOWFLAKE_ACCOUNT` (if saving to Snowflake)

---

## 2. Practice Exam Generator

### 🎯 Purpose
Generate realistic practice exams with multiple-choice questions, explanations, and scoring.

### 📊 Workflow Architecture

```
Webhook → Load Exam Template (Tavily Search) → Generate Questions (LLM) → Format JSON → Return Exam
```

### 🔧 n8n Nodes Setup

#### Node 1: Webhook Trigger
- **Expected Input:**
```json
{
  "user_id": 123,
  "certification": "AWS Certified Solutions Architect - Associate",
  "difficulty": "medium",
  "num_questions": 10,
  "topic": "All Topics" // or specific like "S3", "EC2"
}
```

#### Node 2: Search for Recent AWS Updates (Tavily)
- **Type:** HTTP Request to Tavily API
- **Purpose:** Get latest AWS service updates

```javascript
// Tavily Search Node
{
  "query": `AWS ${$json.topic} exam questions ${$json.certification}`,
  "search_depth": "basic",
  "include_answer": true,
  "max_results": 5
}
```

#### Node 3: Generate Exam Questions (LLM)
- **Type:** LLM Node
- **Prompt:**

```javascript
const certification = $json.certification;
const difficulty = $json.difficulty;
const numQuestions = $json.num_questions;
const topic = $json.topic;
const recentInfo = $json.search_results || "";

const prompt = `Generate ${numQuestions} realistic ${difficulty} practice exam questions for ${certification}.

${topic !== "All Topics" ? `Focus on: ${topic}` : "Cover various AWS services"}

Recent AWS updates to consider:
${recentInfo}

Format each question as JSON:
{
  "question": "Question text",
  "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
  "correct_answer": "A) Option 1",
  "explanation": "Detailed explanation why this is correct",
  "topic": "Service name",
  "difficulty": "${difficulty}"
}

Requirements:
- Questions must be exam-realistic
- Include scenario-based questions
- Provide detailed explanations
- Reference AWS documentation
- Include distractor options that are plausible

Return ONLY a valid JSON array of questions.`;

return { prompt: prompt };
```

#### Node 4: Parse and Validate JSON
- **Type:** Code (JavaScript)

```javascript
const llmResponse = $input.first().json.choices[0].message.content;

// Extract JSON from response
let jsonMatch = llmResponse.match(/\[[\s\S]*\]/);
if (!jsonMatch) {
  // Try to find object array
  jsonMatch = llmResponse.match(/\{[\s\S]*\}/g);
}

let questions = [];
try {
  questions = JSON.parse(jsonMatch[0]);
} catch (e) {
  // Fallback: create error response
  questions = [{
    question: "Error generating questions",
    options: ["A) Please try again"],
    correct_answer: "A) Please try again",
    explanation: "There was an error generating the exam",
    topic: "Error",
    difficulty: "easy"
  }];
}

// Validate and format
const validatedQuestions = questions.map((q, i) => ({
  id: i + 1,
  question: q.question,
  options: q.options,
  correct_answer: q.correct_answer,
  explanation: q.explanation,
  topic: q.topic || "General",
  difficulty: q.difficulty
}));

return {
  exam_id: `exam_${Date.now()}`,
  user_id: $node["Webhook"].json.user_id,
  certification: $node["Webhook"].json.certification,
  questions: validatedQuestions,
  total_questions: validatedQuestions.length,
  created_at: new Date().toISOString()
};
```

#### Node 5: Return Exam
- **Type:** Respond to Webhook
- **Response:** `={{$json}}`

### 🔑 Environment Variables Needed
- `TAVILY_API_KEY`
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

---

## 3. Study Tricks & Mnemonics

### 🎯 Purpose
Generate memory techniques, mnemonics, analogies, and visualization techniques.

### 📊 Workflow Architecture

```
Webhook → Generate Memory Techniques (LLM) → Format Response → Return Tricks
```

### 🔧 n8n Nodes Setup

#### Node 1: Webhook Trigger
- **Expected Input:**
```json
{
  "user_id": 123,
  "certification": "AWS Certified Solutions Architect - Associate",
  "topic": "S3 Storage Classes"
}
```

#### Node 2: Generate Memory Techniques (LLM)
- **Type:** LLM Node
- **Prompt:**

```javascript
const topic = $json.topic;
const certification = $json.certification;

const prompt = `Create comprehensive memory techniques for: "${topic}" (${certification})

Generate the following:

1. **MNEMONIC**: Create a memorable acronym or phrase
2. **ANALOGY**: Compare to real-world scenario
3. **VISUALIZATION**: Describe a mental image
4. **KEY POINTS**: List 5-7 critical points to remember

Format as JSON:
{
  "mnemonic": "Memorable phrase or acronym",
  "analogy": "Real-world comparison",
  "visualization": "Mental image description",
  "key_points": ["Point 1", "Point 2", ...]
}

Example for "S3 Storage Classes":
{
  "mnemonic": "SIGN-OG" - Standard, Intelligent-Tiering, Glacier, Infrequent Access, One Zone, Glacier Deep Archive",
  "analogy": "Like organizing your closet: frequently worn clothes up front (Standard), seasonal clothes on high shelf (IA), old memories in attic (Glacier)",
  "visualization": "Imagine a pyramid: Hot data at top (Standard), cooling as you go down to frozen basement (Glacier)",
  "key_points": [
    "Standard: Most expensive, fastest access",
    "IA: 30-day minimum, for backup",
    "Glacier: Minutes to hours retrieval",
    "Intelligent: Auto-moves based on access"
  ]
}

Return ONLY valid JSON.`;

return { prompt: prompt, topic: topic };
```

#### Node 3: Parse Response
- **Type:** Code (JavaScript)

```javascript
const llmResponse = $input.first().json.choices[0].message.content;
const topic = $node["Webhook"].json.topic;

let tricks = {};
try {
  // Extract JSON
  const jsonMatch = llmResponse.match(/\{[\s\S]*\}/);
  tricks = JSON.parse(jsonMatch[0]);
} catch (e) {
  tricks = {
    mnemonic: "Error generating mnemonic",
    analogy: "Please try again",
    visualization: "Unable to create visualization",
    key_points: ["Error occurred"]
  };
}

return {
  topic: topic,
  ...tricks,
  created_at: new Date().toISOString()
};
```

#### Node 4: Return Response
- **Type:** Respond to Webhook

---

## 4. Answer Evaluation

### 🎯 Purpose
Evaluate written answers with scoring, feedback, and improvement suggestions.

### 📊 Workflow Architecture

```
Webhook → Load Model Answer (LLM) → Evaluate User Answer (LLM) → Score & Feedback → Return Evaluation
```

### 🔧 n8n Nodes Setup

#### Node 1: Webhook Trigger
- **Expected Input:**
```json
{
  "user_id": 123,
  "question": "Explain the difference between S3 and EBS",
  "user_answer": "User's written answer...",
  "certification": "AWS Certified Solutions Architect - Associate"
}
```

#### Node 2: Generate Model Answer (LLM)
- **Type:** LLM Node
- **Prompt:**

```javascript
const question = $json.question;
const certification = $json.certification;

const prompt = `As an expert AWS instructor for ${certification}, provide a MODEL ANSWER for this question:

"${question}"

Your model answer should:
- Be comprehensive yet concise
- Include key technical points
- Reference AWS best practices
- Use clear examples
- Be exam-appropriate

Format: Plain text, 150-250 words.`;

return { prompt: prompt };
```

#### Node 3: Evaluate User Answer (LLM)
- **Type:** LLM Node
- **Prompt:**

```javascript
const question = $node["Webhook"].json.question;
const userAnswer = $node["Webhook"].json.user_answer;
const modelAnswer = $node["Generate Model Answer"].json.choices[0].message.content;

const prompt = `Evaluate this student answer for ${$node["Webhook"].json.certification}.

**QUESTION:**
${question}

**MODEL ANSWER:**
${modelAnswer}

**STUDENT ANSWER:**
${userAnswer}

Provide evaluation as JSON:
{
  "score": 85, // 0-100
  "grade": "B+", // A+, A, B+, B, C+, C, D, F
  "strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "weaknesses": [
    "Weakness 1",
    "Weakness 2"
  ],
  "suggestions": [
    "Suggestion 1",
    "Suggestion 2"
  ],
  "model_answer": "${modelAnswer}",
  "accuracy_score": 80, // Technical correctness
  "completeness_score": 85, // Coverage
  "clarity_score": 90 // How well explained
}

Evaluation criteria:
- Technical accuracy (40%)
- Completeness (30%)
- Clarity and structure (20%)
- Examples and real-world application (10%)

Be constructive and encouraging.`;

return { prompt: prompt };
```

#### Node 4: Parse and Return
- **Type:** Code + Respond to Webhook

```javascript
const llmResponse = $input.first().json.choices[0].message.content;

let evaluation = {};
try {
  const jsonMatch = llmResponse.match(/\{[\s\S]*\}/);
  evaluation = JSON.parse(jsonMatch[0]);
} catch (e) {
  evaluation = {
    score: 0,
    grade: "N/A",
    strengths: [],
    weaknesses: ["Error evaluating answer"],
    suggestions: ["Please try again"],
    model_answer: ""
  };
}

return {
  ...evaluation,
  evaluated_at: new Date().toISOString()
};
```

---

## 5. Q&A Knowledge Base

### 🎯 Purpose
Semantic search over Q&A database with vector embeddings.

### 📊 Workflow Architecture

```
Webhook → Generate Query Embedding → Vector Search (Pinecone/Postgres pgvector) → Return Matches
```

### 🔧 n8n Nodes Setup

#### Node 1: Webhook Trigger
- **Expected Input:**
```json
{
  "query": "S3 pricing",
  "certification": "AWS Certified Solutions Architect - Associate",
  "limit": 10
}
```

#### Node 2: Generate Query Embedding
- **Type:** HTTP Request to OpenAI Embeddings API

```json
{
  "model": "text-embedding-3-small",
  "input": "={{$json.query}}"
}
```

#### Node 3: Vector Search (PostgreSQL pgvector)
- **Type:** Postgres Node
- **Query:**

```sql
SELECT 
  id,
  question,
  answer,
  category,
  tags,
  1 - (embedding <=> '{{$json.embedding}}') as similarity
FROM qa_knowledge_base
WHERE certification = '{{$json.certification}}'
ORDER BY embedding <=> '{{$json.embedding}}'
LIMIT {{$json.limit}};
```

#### Node 4: Return Results
- **Type:** Respond to Webhook

---

## 🚀 Deployment Checklist

### For Each Workflow:

- [ ] Set up webhook with authentication
- [ ] Configure API keys in n8n credentials
- [ ] Test with sample data
- [ ] Set up error handling nodes
- [ ] Add logging/monitoring
- [ ] Configure rate limiting
- [ ] Set webhook URL in Streamlit Cloud secrets

### Recommended n8n Setup:

```toml
# .env for n8n
N8N_ENCRYPTION_KEY=your-encryption-key
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your-postgres-host
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=your-password

# Redis for chat memory
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# LLM APIs
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# Search
TAVILY_API_KEY=your-tavily-key

# Database
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-user
SNOWFLAKE_PASSWORD=your-password
```

---

## 📊 Testing Each Workflow

### 1. Test Chat Workflow
```bash
curl -X POST https://your-n8n-url/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "question": "What is S3?",
    "context": "AWS SAA",
    "timestamp": "2025-12-06T01:00:00Z"
  }'
```

### 2. Test Exam Generator
```bash
curl -X POST https://your-n8n-url/webhook/generate-exam \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "certification": "AWS SAA",
    "difficulty": "medium",
    "num_questions": 5
  }'
```

---

## 💡 Pro Tips

1. **Use Redis for Chat Memory**: Faster than database queries
2. **Cache Common Questions**: Store frequent Q&As in Redis
3. **Rate Limiting**: Protect your API costs
4. **Error Handling**: Always have fallback responses
5. **Logging**: Track usage and costs
6. **Monitoring**: Set up alerts for failures

---

**🎓 Your complete n8n learning platform is ready to build!**

