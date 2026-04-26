# AI-FINAL-MINI-PROJECT

. Challenges Faced (Very Important Section)

Write this properly — this is where you prove engineering maturity

Examples from your project:
Ingredient extraction ambiguity (e.g., “fspinach”, “ricee”)
Synonym handling (tomato vs tomato puree vs canned tomato)
Hard filtering removing valid recipes
Session preference conflicts (exclude vs include chicken)
Poor ranking from vector DB alone
Low dataset coverage (desserts, seafood missing)
OCR not detecting ingredients correctly
LLM hallucination / incorrect intent detection
Performance issues with embedding + API calls
Handling mixed queries (ingredients + intent + exclusions)
🛠️ 3. Solutions Implemented (Map 1:1 with problems)

This is where your project becomes strong.

Example format:

Problem: Exact match failure
Solution: Implemented canonical mapping + fuzzy matching
Problem: Poor ranking
Solution: Hybrid ranking (semantic + rule-based scoring)
Problem: Over-strict filtering
Solution: Introduced soft penalty scoring
Problem: Wrong intent handling
Solution: Added LLM-based NLU + rule fallback
Problem: Missing recipes
Solution: Expanded dataset (desserts + seafood)
Problem: Session inconsistency
Solution: State-aware preference handling
Problem: OCR failure
Solution: Integrated OCR + ingredient extraction pipeline
🧠 4. System Design Decisions (VERY HIGH VALUE)
. Why ChromaDB instead of FAISS
ChromaDB provides built-in persistence and metadata filtering, making it easy to use and integrate. FAISS is more complex and better suited for large-scale, high-performance systems, whereas ChromaDB is ideal for rapid development.

2. Why SentenceTransformers (MiniLM)
MiniLM offers a good balance between speed and semantic accuracy while running efficiently on CPU. It enables fast embedding generation with sufficient performance for real-time applications.

3. Why Groq LLaMA 3 instead of OpenAI
Groq provides ultra-fast inference and is more cost-effective for continuous usage. LLaMA-3 delivers strong performance for intent detection without relying on paid APIs.

4. Why Hybrid Search instead of pure semantic search
Pure semantic search can return irrelevant results due to meaning-based similarity. Hybrid search combines semantic matching with exact ingredient checks, improving accuracy and relevance.

5. Why rule-based fallback with LLaMA 3
LLMs can be inconsistent or fail in structured tasks, so rule-based logic ensures reliability and consistency. This combination provides both accuracy (rules) and flexibility (LLM).

📊 5. Evaluation Metrics (CRITICAL for your “accuracy” claim)

Right now you’re saying “90% accuracy” — but you must justify it.

Add:

Top-1 accuracy (correct recipe appears first)
Top-5 accuracy
Ingredient match percentage
Query success rate
Failure cases

Even simple manual evaluation like:

Query	Expected	Got	Correct?
🔄 6. Iteration Timeline (Evolution of your system)

Show versions like:

v1 → keyword search
v2 → semantic search (ChromaDB)
v3 → hybrid ranking
v4 → NLU + session memory
v5 → soft filtering + dataset expansion

👉 This makes your project look industry-level

🚫 7. Limitations (Don’t skip this)

Be honest:

Small dataset → limited diversity
OCR accuracy depends on image quality
LLM latency & cost
No real-time user feedback loop
Limited personalization
🚀 8. Future Enhancements (Make it look “Google-level”)

Add ideas like:

LLM-based reranking (you’re about to add this)
Auto recipe generation if no match found
Nutrition analysis
Voice input
Reinforcement learning from user feedback
Large-scale dataset (100K+ recipes)
Multilingual support
🧩 9. Demo Scenarios (Very useful for presentation)

Show:

“I have chicken, rice” → good result
“No chicken” → filter works
“Include chicken again” → override works
OCR input → detects ingredients
Substitution query → gives alternatives
🎯 10. Key Learnings (Interview gold)

Write what you learned:

Hybrid systems outperform pure AI or pure rules
Data quality > model complexity
LLMs are powerful but need constraints
Ranking is the hardest part of recommendation systems
Handling user intent is more complex than expected

🚀 Core Features
Ingredient-based recipe search (input text or list)
Multi-ingredient matching with relevance scoring
Support for inclusion & exclusion (e.g., “no chicken”)
Cuisine, diet, and meal-type awareness
Step-by-step recipe instructions
🧠 AI-Powered Features
LLM-based intent detection (understands natural language queries)
Semantic search using embeddings (understands meaning, not just keywords)
LLM-based re-ranking for final result optimization
Smart explanation generation for top recipe selection
⚙️ Advanced Search & Ranking
Hybrid search (semantic + keyword + rule-based scoring)
Soft penalty system instead of hard filtering
Multi-ingredient bonus scoring for better ranking
Ingredient highlighting (matched vs missing)
Seafood grouping logic (fish/prawn → all seafood recipes)
🔄 Personalization & State Handling
Session-based memory for user preferences
Dynamic preference override (e.g., “include chicken again”)
Persistent exclusion handling across queries
🔍 Ingredient Intelligence
Canonical ingredient mapping (handles synonyms & variations)
Fuzzy matching for noisy inputs (e.g., “fspinach”)
Ingredient extraction from free text queries
🔁 Substitution System
Ingredient substitution suggestions (e.g., salmon → tofu)
Context-aware replacements (veg/non-veg alternatives)
📷 OCR & Multimodal Input
Image-to-ingredient detection using OCR
Dual OCR pipeline (EasyOCR + Tesseract fallback)
Image preprocessing (contrast + sharpening)
📚 Dataset & Coverage
Expanded dataset (50+ recipes across cuisines)
Includes desserts, seafood, vegetarian, vegan dishes
Balanced coverage for real-world queries
🛡️ Reliability Features
Rule-based fallback when LLM fails
Hybrid NLU (LLM + regex-based backup)
Error handling for API failures
Cached embeddings for faster startup
🎯 UX Features
Match percentage scoring
Missing ingredient suggestions
Clean recipe cards with structured output
Real-time responses

WORK FLOW
User Query →
Intent Detection →
Ingredient Extraction →
Constraint Filtering →
Candidate Retrieval (ChromaDB) →
Rule-based Scoring →
LLM Re-ranking →
Final Output / Fallback Generation

| Version          | Accuracy (Approx) | Key Features                                                                                                                                    | Major Limitations                           |
| ---------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| **v1**           | ~40%              | Basic keyword search                                                                                                                            | Exact match only, fails on natural language |
| **v2**           | ~60%              | Semantic search (ChromaDB + embeddings)                                                                                                         | Poor ranking, irrelevant results            |
| **v3**           | ~70–75%           | Hybrid search (semantic + rules)                                                                                                                | Hard filtering removed valid recipes        |
| **v4**           | ~80%              | Session memory + preferences (exclude/include)                                                                                                  | Intent queries still failing                |
| **v5**           | ~85%              | Soft scoring, dataset expansion, LLM reranking, OCR                                                                                             | No intent understanding, generation broken  |
| **v6 (Current)** | **~90–92%**       | ✅ Intent-based filtering  <br> ✅ AI generation fallback (fixed) <br> ✅ Contradiction handling <br> ✅ Meal-type tagging <br> ✅ Code optimization | Minor edge cases, limited dataset scale     |


questions for demo:
quick dinner recipe
chicken and rice
i want a recipe using fish,prawn, beef,prawn
I have rice, want spicy, vegetarian dinner under 30 min no chicken recipes
no chicken reset preferences
quick dinner
desseert using banana
i want a dessert recipe
spinach recipe for breakfast
OCR
i have onion,tomato,chilli,pepper,salt,garlic,cauliflower
random veg recipe
Generate a vegetarian alternative to fish recipe


AFTER DOWNLOADING / EXTRACTING PROJECT (SETUP GUIDE)

When you use this project on another PC:

✅ 1. Open terminal in project folder
cd AI-FINAL-MINI-PROJECT
✅ 2. Create virtual environment
python -m venv venv
✅ 3. Activate it

Windows:

venv\Scripts\activate
✅ 4. Install dependencies
pip install -r requirements.txt
✅ 5. Setup environment variables

Create .env file:

GROQ_API_KEY=your_api_key
✅ 6. Run backend
python backend.py

1. GO TO FRONTEND FOLDER
cd frontend
✅ 2. INSTALL DEPENDENCIES
npm install
