# 🤖 Multi-Agent AI Research Assistant

An intelligent multi-agent research system built with **Python, LangChain, LangGraph, Ollama, Tavily, BeautifulSoup, and Streamlit**. The system automates the research workflow by using specialized AI agents to search the web, scrape relevant sources, generate a structured research report, and critically review the final output.

### 🚀 How It Works

The research pipeline consists of four main stages:

1. 🔎 **Search Agent** — Searches the web for recent, reliable, and detailed information using Tavily.
2. 📖 **Reader Agent** — Selects a relevant source and scrapes its content for deeper research.
3. ✍️ **Writer Agent** — Combines the gathered information and generates a professional research report with key findings, conclusions, and sources.
4. 🧐 **Critic Agent** — Reviews the generated report, identifies strengths and areas for improvement, and provides a structured evaluation.

The complete pipeline can be executed from the terminal, while the **Streamlit web interface** provides an interactive experience with live progress, previous-search history, detailed research results, critic feedback, and Markdown report downloads. 

### 🛠️ Tech Stack

- **Python**
- **LangChain**
- **LangGraph**
- **Ollama / Qwen 3.5 4B**
- **Tavily Search API**
- **BeautifulSoup**
- **Requests**
- **Streamlit**
- **Pydantic**
- **python-dotenv**

The project uses environment variables for configuration and includes dependencies for LLM orchestration, web search, web scraping, HTTP requests, and development workflows.

### ✨ Key Features

- Multi-agent research workflow
- Real-time web search
- Automated source scraping
- AI-generated research reports
- Automated report criticism and feedback
- Interactive Streamlit interface
- Search history
- Markdown report download
- Local LLM support through Ollama
- Modular agent and tool architecture

### 📂 Project Structure

```text
├── agents.py          # AI agents, writer and critic chains
├── pipeline.py        # Core research pipeline
├── tools.py           # Web search and web scraping tools
├── app.py             # Streamlit user interface
├── requirements.txt   # Project dependencies
└── .env               # API keys and environment configuration
```

### 🎯 Purpose

This project demonstrates how **multiple specialized AI agents can collaborate to automate an end-to-end research workflow**, reducing the manual effort required to search, analyze, write, and review research content.
