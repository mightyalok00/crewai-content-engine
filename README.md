# 🤖 CrewAI YouTube-to-Blog Multi-Agent System (Google AI Studio Edition v3.5)

An automated 9-agent autonomous workflow built with **CrewAI** that transcribes, analyzes, drafts, fact-checks & code-reviews technical YouTube videos into publish-ready blog posts, generates 1200x630 HD cover banner art, and creates viral SEO & social media distribution kits using the **Google AI Studio Gemini API**.

---

## 🏗️ 9-Agent Architecture & Workflow

```mermaid
graph LR
    User[Topic / YouTube URL / Channel] --> Researcher[1. Senior Content Researcher]
    Researcher -->|Extracts Transcript & Insights| YT[YouTube Universal Tool]
    YT -->|Raw Video Insights| Researcher
    Researcher -->|Structured Brief| Verifier[2. Web & Benchmark Cross-Verifier]
    Verifier --> Writer[3. Senior Content Writer]
    Writer --> Diagrammer[4. Mermaid Architecture Diagrammer]
    Diagrammer --> CodeQA[5. Code QA Sandbox]
    CodeQA --> Editor[6. Editor-in-Chief]
    Editor --> SEO[7. SEO & Social Specialist]
    SEO --> Podcast[8. Podcast Audio Producer]
    Podcast --> Newsletter[9. Substack Newsletter Copywriter]
    Newsletter --> Output[Multi-Channel Markdown Artifacts]
    Output --> CoverGen[🎨 AI Cover Art Engine]
```

1. **Researcher Agent (`blog_researcher`)**: Uses `yt_tool` to locate video transcripts and extract deep technical insights.
2. **Cross-Verification Agent (`cross_verifier_agent`)**: Cross-checks facts, benchmark numbers, and API syntax against documentation.
3. **Writer Agent (`blog_writer`)**: Transforms technical insights into a comprehensive draft markdown blog post.
4. **Diagrammer Agent (`diagram_agent`)**: Generates production-ready Mermaid.js architecture diagrams and workflow visualizers.
5. **Code QA Agent (`code_qa_agent`)**: Validates code snippets, adds type annotations and dependencies.
6. **Editor-in-Chief (`editor_agent`)**: Integrates diagrams, code, and narrative into a finalized master post.
7. **SEO & Social Specialist Agent (`seo_social_agent`)**: Converts the finalized article into viral LinkedIn posts, Twitter/X threads, high-intent SEO tags, and executive summaries.
8. **Podcast Audio Producer (`podcast_agent`)**: Crafts 2-host conversational dialogue and solo voiceover scripts.
9. **Newsletter Copywriter (`newsletter_agent`)**: Writes high-converting email newsletter editions.
10. **AI Cover Art Generator (`image_gen.py`)**: Automatically renders a 1200x630 HD hero banner in 4 selectable aesthetic styles.
11. **Contextual Memory Engine**:
    - **Short-Term Memory**: Shared RAG context between agents during task execution.
    - **Long-Term Memory**: Historical knowledge and previous article insights preserved across sessions.
    - **Entity Memory**: Identifies technical terms, authors, and frameworks for consistency.
    - **Embedder Support**: Local zero-cost ONNX embeddings (default), Google AI embeddings, or OpenAI embeddings.

---

## 📁 Project Structure

```text
├── .env.example          # Environment variables template
├── .env                  # Local Google AI Studio & Memory configuration
├── requirements.txt      # Python dependencies
├── tools.py              # YouTube Transcript & Channel Extraction Tool
├── agents.py             # 9 Autonomous CrewAI Agents
├── tasks.py              # 9 Sequenced CrewAI Tasks
├── image_gen.py          # AI Banner & Cover Art Generation Engine (1200x630 HD)
├── crew.py               # Assembles 9-Agent Crew with multi-tier memory
├── app.py                # FastAPI Web Server with Memory API, Cover Gen & Exports
├── static/
│   ├── index.html        # Glassmorphic UI with 9-Agent Visualizer, Cover Studio & Social Kit
│   ├── style.css         # Styling, Cover Studio Grid & Layout
│   └── app.js            # Real-time SSE streams, 9-Agent transitions & Webhooks
├── new_blog_post.md      # Generated blog article output
├── social_snippets.md    # Generated SEO & Social Media Kit
├── podcast_script.md     # Generated Podcast Dialogue Script
└── newsletter.md         # Generated Email Newsletter Issue
```

---

## 🚀 Quickstart Guide

### 1. Create and Activate Virtual Environment

```bash
# Using venv
python -m venv venv
venv\Scripts\activate   # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Google AI Studio / Gemini API Key

Edit [.env](file:///e:/crew/.env) and set your Gemini API key:

```env
GEMINI_API_KEY=AQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gemini/gemini-3.8-flash
```

---

## 💻 Running the Application

### Option A: Interactive Web UI Studio (Recommended)

Start the modern web studio:

```bash
python app.py
```

Then open **[http://localhost:8000](http://localhost:8000)** in your browser to:

- 🎯 **Topic & Source Selector**: Switch channels (`@krishnaik06`, `@freecodecamp`, `@lexfridman`, `@hubermanlab`) or enter direct YouTube URLs.
- ⚡ **Real-Time 9-Agent Flow**: Watch live animated node status indicators and terminal logs via Server-Sent Events.
- 📱 **SEO & Social Media Kit**: 1-click copy formatted LinkedIn posts, Twitter/X threads, and SEO tags.
- 🎙️ **Podcast Studio**: Synthesize and listen to 2-host audio scripts with browser speech synthesis.
- 📧 **Newsletter Suite**: Export ready-to-send Substack and Beehiiv email campaigns.
- 📤 **Export Suite**:
  - Download `.md` raw Markdown.
  - Download standalone styled `.html` with code syntax highlighting.
  - 🖨️ Clean print or save as `.pdf`.
  - 🚀 Dispatch directly to any Webhook (Zapier, Make, n8n, Slack, Dev.to).

---

### Option B: Command-Line Interface (CLI)

Run with the default topic and channel:

```bash
python crew.py
```

Or pass custom topic and channel arguments:

```bash
python crew.py "LangChain vs CrewAI" "@freecodecamp"
```


## 🛡️ Production Engineering Upgrade

The project now includes a production-hardening layer while keeping the existing Studio UI and 9-agent workflow intact.

### Security
- API keys are never returned by GET /api/settings; the response exposes only api_key_configured.
- Admin/settings/export/webhook operations are localhost-restricted by default.
- Remote admin access requires APP_API_TOKEN and a Bearer token.
- CORS defaults to localhost origins instead of wildcard access.
- Webhook URLs are validated against private, loopback, link-local, multicast, and reserved addresses.
- Webhook redirects are disabled to reduce SSRF risk.
- Request models enforce size and enum constraints with Pydantic.

### Quality Engineering
- models.py provides typed contracts for research, evidence, verification, quality reports, and artifacts.
- quality_gate.py provides a deterministic post-generation quality score and blockers for future regeneration loops.
- tests/ covers the security boundary, Pydantic validation, and quality-gate behavior.
- .github/workflows/ci.yml runs syntax checks and tests on Python 3.11 and 3.12.
- .github/workflows/security.yml runs scheduled pip-audit dependency checks.

### Local configuration
Copy .env.example to .env. For a local-only installation, leave APP_API_TOKEN empty. If the application is exposed through a reverse proxy or network interface, set a strong token and restrict the proxy/firewall as well.