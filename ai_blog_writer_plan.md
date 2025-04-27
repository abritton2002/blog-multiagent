
# 📚 Full Build Plan for Local Multi-Agent Blog Writing App

This markdown file details **every step** needed to build your local, private, free, open-source multi-agent blog writing system, ready for execution inside Cursor IDE.

---

# ✨ Overview

**Goal**: Build a local Streamlit app that:
- Takes a blog topic
- Researches online using Linkup
- Summarizes key findings
- Writes a full blog post in your personalized voice and structure
- Lets you export the blog as a file

**Main Tools**:
- **Streamlit**: User interface
- **CrewAI**: Multi-agent orchestration
- **Ollama**: Local LLM hosting (DeepSeek, Llama3, etc.)
- **Linkup**: Local deep search API
- **Python 3.11+**

---

# 🔍 Project Directory Structure

```plaintext
/ai-blog-writer
    /agents
        web_search_agent.py
        research_agent.py
        writer_agent.py
    /prompts
        alex_voice_style.md
        alex_blog_prompt.md
    /streamlit_app
        app.py
    /utils
        linkup_api.py
        formatting_helpers.py
    README.md
    requirements.txt
```

---

# 🚀 Step-by-Step Setup

## 1. Install Environment

```bash
pip install streamlit crewai
brew install ollama  # or Windows/Linux alternatives
```

## 2. Install Linkup API (Deep Web Search)

- Clone and run [Linkup](https://github.com/linkup-ai/linkup).
- Follow Docker setup instructions.

## 3. Download Local LLMs with Ollama

```bash
ollama run deepseek
ollama run llama3
```

---

# 🤖 Agent Development (CrewAI)

## Web Search Agent (`agents/web_search_agent.py`)

```python
from crewai import Agent

web_search_agent = Agent(
    role="Deep Research Specialist",
    goal="Find high-quality information about a given topic.",
    backstory="Master researcher using Linkup.",
    model="ollama:deepseek"
)
```

## Research Summarizer Agent (`agents/research_agent.py`)

```python
from crewai import Agent

research_agent = Agent(
    role="Research Analyst",
    goal="Summarize findings into actionable points.",
    backstory="Clusters insights clearly.",
    model="ollama:deepseek"
)
```

## Writer Agent (`agents/writer_agent.py`)

```python
from crewai import Agent

with open('../prompts/alex_blog_prompt.md', 'r') as f:
    blog_prompt = f.read()

writer_agent = Agent(
    role="Personal Blogger",
    goal="Write a blog post in Alex's style.",
    backstory="Substack blogger who simplifies AI.",
    model="ollama:deepseek",
    system_prompt=blog_prompt
)
```

---

# 🛠 Utility Scripts

## Linkup API Helper (`utils/linkup_api.py`)

```python
import requests

def search_linkup(query):
    url = "http://localhost:8000/search"
    params = {"q": query}
    response = requests.get(url, params=params)
    return response.json()
```

## Formatting Helper (`utils/formatting_helpers.py`)

```python
def format_blog_output(blog_text):
    return blog_text.replace('\n', '\n\n')
```

---

# 🎨 Streamlit App (`streamlit_app/app.py`)

```python
import streamlit as st
from utils.linkup_api import search_linkup
from agents.web_search_agent import web_search_agent
from agents.research_agent import research_agent
from agents.writer_agent import writer_agent
from utils.formatting_helpers import format_blog_output

st.title("🔍 AI Blog Generator - Local & Private")

topic = st.text_input("Enter your blog topic:")

if st.button("Generate Blog"):
    if topic:
        st.write("Searching the web...")
        search_results = search_linkup(topic)

        st.write("Analyzing research...")
        research_summary = research_agent.run(input=search_results)

        st.write("Writing blog post...")
        final_blog = writer_agent.run(input=research_summary)

        st.markdown(format_blog_output(final_blog))

        st.download_button("Download Blog", final_blog, file_name="blog_post.md")
    else:
        st.warning("Please enter a topic first.")
```

---

# ✅ Full To-Do Checklist

- [ ] Install Python 3.11+
- [ ] Install Streamlit, CrewAI, Ollama
- [ ] Host Linkup locally
- [ ] Download DeepSeek or Llama3 model
- [ ] Build agents and utilities
- [ ] Build Streamlit app
- [ ] Test first full blog run

---

# 🚀 First Blog Run Example

1. Launch Streamlit app.
2. Enter: `Latest Open-Source AI Trends 2025`
3. Generate Blog.
4. Download `.md` file.

---

# 📦 Requirements.txt

```plaintext
streamlit
crewai
requests
```

---

# 🌟 You're ready to build your AI-powered blogging machine!
