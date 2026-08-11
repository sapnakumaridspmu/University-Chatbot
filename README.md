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