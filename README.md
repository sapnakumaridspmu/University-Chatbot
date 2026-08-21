# 🎓 University Chatbot

An AI-powered University Assistant Chatbot designed to provide users with university-related information through a conversational interface.

## 📌 About the Project

University Chatbot is an AI-based assistant that helps users access university information through natural language queries.

The project includes a chatbot agent, database layer, LLM integration, and a data ingestion pipeline for collecting and managing university information.

## ✨ Key Features

- 🤖 AI-powered conversational chatbot
- 🔎 University information retrieval
- 🧠 Agent-based chatbot workflow
- 🗄️ Database integration
- 🌐 University website data scraping
- 🏫 Faculty and programme information ingestion
- 🛠️ Tool-based chatbot architecture
- 🔐 Environment-based configuration

## 🛠️ Technologies Used

- Python
- LLM / Generative AI
- Agent-based architecture
- Web Scraping
- Database
- HTML
- Git & GitHub

## 🚀 Deploying on Render

This is a **Streamlit** app, so Render needs to be told explicitly how to build and run it (it does not auto-detect Streamlit).

1. **Build Command**
   ```
   pip install -r requirements.txt
   ```
   (A root-level `requirements.txt` — copied from `chatbot/requirements.txt` — and a `Procfile` are included so Render's default Python auto-detect works out of the box.)

2. **Start Command** (already set via `Procfile`, but you can also paste this directly in Render → Settings → Start Command)
   ```
   streamlit run chatbot/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

3. **Environment Variables** — set these under Render → Environment (do NOT commit a real `.env`, it's git-ignored on purpose):
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT` → must point to an **externally reachable** MySQL database (Render has no local MySQL). `localhost` will never work in production — use a hosted MySQL like Railway, Aiven, PlanetScale, Clever Cloud, or TiDB Cloud.
   - `LLM_PROVIDER`, `LLM_MODEL` → e.g. `openai` / `gpt-4o-mini`
   - The matching API key: `OPENAI_API_KEY` (or `GOOGLE_API_KEY`/`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY` depending on `LLM_PROVIDER`)
   - `TAVILY_API_KEY` → optional, but without it the web-search fallback tool is disabled and the bot can only answer from the faculty DB + the model's own knowledge.

4. **Populate the database.** The `faculty` table must actually contain BBAU data on whatever MySQL instance you point `DB_HOST` to. Run `ingestion/insert_faculty_to_db.py` (after updating its hardcoded local connection details) against your **production** database, not just your local one — otherwise faculty queries on the deployed bot will come back empty even though the code itself works fine.

## 📁 Project Structure

```text
chatbot-univ/
│
├── chatbot/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── prompts.py
│   │   ├── state.py
│   │   └── tools.py
│   │
│   ├── db/
│   │   ├── connection.py
│   │   └── queries.py
│   │
│   ├── app.py
│   ├── config.py
│   ├── llm_factory.py
│   └── requirements.txt
│
├── data/
│
├── ingestion/
│   ├── admin_scraper.py
│   ├── administration_tools.py
│   ├── faculty_scraper.py
│   ├── insert_faculty_to_db.py
│   ├── programme_scraper.py
│   └── scrape.py
│
├── .env.template
├── .gitignore
└── README.md