#  Agentic AI Blog Pipeline — MCP + Groq + Python

> **Automatically research, write, and publish blog posts using 3 MCP Servers and Groq LPU inference.**
> One command. 11 tool calls. ₹0.50 per article. Zero Claude. Zero OpenAI.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LPU%20Inference-orange?logo=groq)](https://groq.com)
[![MCP](https://img.shields.io/badge/MCP-1.26.0%2B-green)](https://modelcontextprotocol.io)
[![Model](https://img.shields.io/badge/Model-llama--3.3--70b--versatile-purple)](https://console.groq.com)
[![Cost](https://img.shields.io/badge/Cost-₹0.50%2Farticle-brightgreen)](https://console.groq.com)

---

##  What This Does

```
python orchestrator_groq.py "Oracle DBA best practices for AI"
```

That single command autonomously triggers **3 MCP servers** across **11 tool calls** and delivers:

| Output File | Description |
|---|---|
| `your-topic_20260315_143022.html` | Styled, publication-ready blog post |
| `wp_export_your-topic_20260315.xml` | WordPress WXR import file |
| `pipeline_report_20260315_143022.json` | Run summary with SEO snapshot |

**Total time: 2–4 minutes. Total cost: ~₹0.50.**

---

##  Architecture

```
YOU
 │
 ▼
orchestrator_groq.py          ← MCP CLIENT (hardcoded tool sequence)
 │
 ├──► server1_researcher_groq.py   ← MCP SERVER 1: Research Agent
 │         search_wikipedia()
 │         get_hackernews_top()
 │         get_devto_articles()
 │         compile_research()
 │         [No LLM — free public APIs]
 │
 ├──► server2_writer_groq.py       ← MCP SERVER 2: Writer Agent
 │         generate_blog_outline()
 │         generate_blog_content()     ← Groq llama-3.3-70b-versatile
 │         generate_seo_metadata()
 │         package_for_publisher()
 │         [Groq API — 500 TPS on LPU]
 │
 └──► server3_publisher_groq.py    ← MCP SERVER 3: Publisher Agent
           save_local_html()
           generate_wordpress_export()
           generate_pipeline_report()
           [No LLM — local file I/O]
```

---

##  Project Structure

```
mcp-blog-pipeline/
│
├── orchestrator_groq.py          # ← RUN THIS — MCP client driving all 3 servers
├── server1_researcher_groq.py    # MCP Server 1 — Wikipedia, HackerNews, DEV.to
├── server2_writer_groq.py        # MCP Server 2 — Groq API blog writing
├── server3_publisher_groq.py     # MCP Server 3 — Save HTML + WordPress XML
├── how_to_run.txt                # Quick start reference
└── README.md                     # This file
```

**Output folder** (auto-created on first run):
```
~/blog-pipeline-output/
├── your-topic_YYYYMMDD_HHMMSS.html
├── wp_export_your-topic_YYYYMMDD_HHMMSS.xml
└── pipeline_report_YYYYMMDD_HHMMSS.json
```

---

##  Quick Start

### 1. Prerequisites

- Python 3.11 or 3.12
- Git Bash (Windows) or any Unix terminal
- Groq API key from [console.groq.com](https://console.groq.com)

### 2. Install Dependencies

```bash
pip install "mcp[cli]" groq
```

Verify:
```bash
python -c "import mcp; print('MCP OK')"
python -c "from groq import Groq; print('Groq OK')"
```

### 3. Set Your Groq API Key

```bash
# Add permanently to ~/.bashrc
echo 'export GROQ_API_KEY="gsk_your_key_here"' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $GROQ_API_KEY   # Must show gsk_...
```

### 4. Clone and Run

```bash
git clone https://github.com/mshan011181/mcp-blog-pipeline.git
cd mcp-blog-pipeline

python orchestrator_groq.py "Your blog topic here"
```

### 5. View Output

```bash
# Windows
explorer ~/blog-pipeline-output

# Linux/Mac
open ~/blog-pipeline-output
```

---

##  Example Topics

```bash
# Oracle DBA
python orchestrator_groq.py "Oracle DBA best practices for AI workload integration"
python orchestrator_groq.py "How to monitor Oracle Database using AI-powered dashboards"

# AI Engineering
python orchestrator_groq.py "Building RAG systems with ChromaDB and Python"
python orchestrator_groq.py "MCP protocol explained for backend developers"

# Cloud + Infrastructure
python orchestrator_groq.py "Deploying AI agents on Google Cloud Run"
python orchestrator_groq.py "Groq LPU vs GPU for enterprise AI inference"
```

---

##  Configuration

All settings are in the **CONFIG block** at the top of `orchestrator_groq.py`:

```python
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
ORCHESTRATOR_MODEL = "llama-3.1-8b-instant"    # Fast decisions — 840 TPS
WRITER_MODEL       = "llama-3.3-70b-versatile"  # Best writing — 500 TPS
TARGET_AUDIENCE    = "Oracle DBA and AI engineer exploring agentic systems"
BLOG_NAME          = "shanmaha.com"
```

### Switch Writer Model Without Editing Code

```bash
GROQ_WRITER_MODEL="qwen/qwen3-32b" python orchestrator_groq.py "your topic"
```

---

##  MCP Servers — What Each One Does

### Server 1 — Research Agent (`server1_researcher_groq.py`)

| Tool | What It Does | API Used |
|---|---|---|
| `search_wikipedia(topic)` | Gets factual background summary | Wikipedia REST API (free) |
| `get_hackernews_top(limit)` | Gets trending tech stories | HackerNews Firebase API (free) |
| `get_devto_articles(tag, limit)` | Gets recent community posts | DEV.to API (free) |
| `compile_research(...)` | Bundles everything into JSON for Writer | No API — local Python |

**No Groq calls. No API keys needed. 100% free.**

---

### Server 2 — Writer Agent (`server2_writer_groq.py`)

| Tool | What It Does | Groq Call? |
|---|---|---|
| `generate_blog_outline(research_json)` | Creates structured outline |  Yes |
| `generate_blog_content(topic, outline, ...)` | Writes full 1,200-word HTML post |  Yes |
| `generate_seo_metadata(topic, content)` | Generates title, slug, tags, description |  Yes |
| `package_for_publisher(...)` | Bundles blog + SEO into final JSON |  No |

**Model: `llama-3.3-70b-versatile` at 500 TPS on Groq LPU.**
**This is where ALL writing happens.**

---

### Server 3 — Publisher Agent (`server3_publisher_groq.py`)

| Tool | What It Does | Groq Call? |
|---|---|---|
| `save_local_html(package_json)` | Saves styled HTML file to disk |  No |
| `generate_wordpress_export(package_json)` | Creates WordPress WXR XML file |  No |
| `publish_to_devto(package_json)` | Posts to DEV.to (requires DEVTO_API_KEY) |  No |
| `generate_pipeline_report(...)` | Saves JSON run summary |  No |

**No Groq calls. Pure Python file I/O.**

---

##  Cost Breakdown

| Component | Model | Cost Per Run |
|---|---|---|
| Orchestration decisions | `llama-3.1-8b-instant` | ~₹0.04 |
| Blog writing (4 Groq calls) | `llama-3.3-70b-versatile` | ~₹0.46 |
| Research (Wikipedia/HN/DEV.to) | No LLM | ₹0.00 |
| File saving | No LLM | ₹0.00 |
| **Total per article** | | **~₹0.50** |

### At Scale

| Volume | This Pipeline | Claude Sonnet | Annual Saving |
|---|---|---|---|
| 50 articles/month | ~₹25 | ~₹600 | **₹6,900/year** |
| 100 articles/month | ~₹50 | ~₹1,200 | **₹13,800/year** |

---

##  Groq Models Reference

| Model ID | Speed | Role | Cost (in/out per 1M) |
|---|---|---|---|
| `llama-3.1-8b-instant` | 840 TPS | Orchestrator decisions | $0.05 / $0.08 |
| `llama-3.3-70b-versatile` | 500 TPS | Blog writing  default | $0.59 / $0.79 |
| `qwen/qwen3-32b` | 662 TPS | Alternative writer | $0.29 / $0.59 |

>  **Note:** `llama3-70b-8192` was deprecated by Groq on May 31, 2025.
> Use `llama-3.3-70b-versatile` as the replacement.

---

## Windows-Specific Notes

The orchestrator includes automatic Windows fixes:

```python
# UTF-8 encoding for terminal output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ProactorEventLoop required for MCP subprocess pipes on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

**Run from Git Bash** (not Windows CMD or PowerShell) for best compatibility.

---

## 🔌 DEV.to Publishing (Optional)

To auto-publish to DEV.to, set your API key:

```bash
export DEVTO_API_KEY="your_devto_api_key"
```

Get your key at: [dev.to/settings/extensions](https://dev.to/settings/extensions)

The `publish_to_devto()` tool in Server 3 will post as a **draft** by default.

---

## 🛠️ Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `model_decommissioned: llama3-70b-8192` | Old model name | Change to `llama-3.3-70b-versatile` in server2 |
| `ERROR: GROQ_API_KEY not set` | Variable not loaded | Run `source ~/.bashrc` |
| `AuthenticationError 401` | Wrong API key | Regenerate at console.groq.com/keys |
| `MCP server EOF error` | Server crashed on startup | Run `python server1_researcher_groq.py` directly to see error |
| `HTML file shows Groq error` | API error saved as content | Fix model name / key, then rerun |
| `Pipeline hangs on Phase 2` | Groq timeout on large prompt | Reduce `word_count` to 800 |
| `asyncio RuntimeError` (Windows) | Wrong event loop | Already fixed in orchestrator — ensure you're on Python 3.11+ |

### Test Your Setup

```bash
# 1. Test Groq API key
python -c "
from groq import Groq; import os
c = Groq(api_key=os.environ.get('GROQ_API_KEY',''))
r = c.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role':'user','content':'reply: GROQ OK'}],
    max_tokens=10
)
print(r.choices[0].message.content)
"

# 2. Test MCP Server 1 loads
python server1_researcher_groq.py
# Press Ctrl+C after 2 seconds — no error = working
```

---

## 📋 Requirements

```
mcp[cli]>=1.26.0
groq>=0.9.0
```

**Standard library only — no other packages needed:**
`asyncio`, `json`, `os`, `sys`, `urllib.request`, `re`, `datetime`

---

## 🚀 Pipeline Output Example

```
════════════════════════════════════════════════════════════
  shanmaha.com Blog Auto-Pipeline (Groq Edition)
  Topic: Oracle DBA best practices for AI workload integration
  Orchestrator: llama-3.1-8b-instant
  Writer: llama-3.3-70b-versatile
════════════════════════════════════════════════════════════

PHASE 1: RESEARCH AGENT (Server 1)
  [Researcher] -> Calling: search_wikipedia     OK Got 1,284 chars
  [Researcher] -> Calling: get_hackernews_top   OK Got 892 chars
  [Researcher] -> Calling: get_devto_articles   OK Got 734 chars
  [Researcher] -> Calling: compile_research     OK Got 2,341 chars

PHASE 2: WRITER AGENT (Server 2)
  [Writer] -> Calling: generate_blog_outline    OK Got 1,823 chars
  [Writer] -> Calling: generate_blog_content    OK Got 9,241 chars
  [Writer] -> Calling: generate_seo_metadata    OK Got 412 chars
  [Writer] -> Calling: package_for_publisher    OK Got 11,203 chars

PHASE 3: PUBLISHER AGENT (Server 3)
  [Publisher] -> Calling: save_local_html             OK
  [Publisher] -> Calling: generate_wordpress_export   OK
  [Publisher] -> Calling: generate_pipeline_report    OK

════════════════════════════════════════════════════════════
  PIPELINE COMPLETE!
  oracle-dba-ai_20260315_143022.html    (24,381 bytes)
  wp_export_oracle-dba-ai_20260315.xml  (19,204 bytes)
  pipeline_report_20260315_143022.json  (612 bytes)
════════════════════════════════════════════════════════════
```

---

## 👤 Author

**Shanmugavelu** — Oracle DBA + AI Engineer
- 🌐 [shanmaha.com](https://shanmaha.com)
- 💼 [LinkedIn](https://linkedin.com/in/shanmugavelu)
- 🐙 [GitHub](https://github.com/mshan011181)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## If This Helped You

Give this repo a ⭐ and share your generated articles!

Built with  using **MCP + Groq + Python** — proving that powerful AI pipelines don't need to cost a fortune.
