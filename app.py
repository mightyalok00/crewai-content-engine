import asyncio
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from security import require_local_admin, safe_webhook_url, post_json

# Configure UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(override=True)

app = FastAPI(title="CrewAI Studio API", version="3.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
OUTPUT_FILE = BASE_DIR / "new_blog_post.md"
SOCIAL_FILE = BASE_DIR / "social_snippets.md"
PODCAST_FILE = BASE_DIR / "podcast_script.md"
NEWSLETTER_FILE = BASE_DIR / "newsletter.md"
ENV_FILE = BASE_DIR / ".env"

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    channel: str = Field("@krishnaik06", max_length=500)


class YouTubeInspectRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)


class SettingsRequest(BaseModel):
    api_key: str = Field(..., min_length=10, max_length=500)
    model_name: str = Field(..., min_length=1, max_length=200)
    memory_enabled: bool = True
    embedder_provider: str = Field("onnx", pattern="^(onnx|google|openai)$")


class WebhookPublishRequest(BaseModel):
    webhook_url: str = Field(..., min_length=8, max_length=2048)
    topic: str
    channel: str = ""
    markdown_content: str
    social_content: str = ""
    podcast_content: str = ""
    newsletter_content: str = ""


class CoverGenerateRequest(BaseModel):
    topic: str
    channel: str = "@krishnaik06"
    style_key: str = "3d_tech"


class HtmlExportRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    html_body: str = Field(..., min_length=1, max_length=2_000_000)


@app.post("/api/youtube/inspect")
async def api_inspect_youtube(req: YouTubeInspectRequest):
    from tools import inspect_youtube_url

    return inspect_youtube_url(req.url)


@app.get("/api/youtube/inspect")
async def api_inspect_youtube_get(url: str):
    from tools import inspect_youtube_url

    return inspect_youtube_url(url)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/style.css")
async def get_css():
    return FileResponse(STATIC_DIR / "style.css")


@app.get("/app.js")
async def get_js():
    return FileResponse(STATIC_DIR / "app.js")


@app.get("/api/article")
async def get_latest_article():
    article_content = None
    social_content = None
    podcast_content = None
    newsletter_content = None

    if OUTPUT_FILE.exists():
        article_content = OUTPUT_FILE.read_text(encoding="utf-8", errors="replace")
    if SOCIAL_FILE.exists():
        social_content = SOCIAL_FILE.read_text(encoding="utf-8", errors="replace")
    if PODCAST_FILE.exists():
        podcast_content = PODCAST_FILE.read_text(encoding="utf-8", errors="replace")
    if NEWSLETTER_FILE.exists():
        newsletter_content = NEWSLETTER_FILE.read_text(encoding="utf-8", errors="replace")

    return {
        "content": article_content,
        "social": social_content,
        "podcast": podcast_content,
        "newsletter": newsletter_content,
    }


@app.get("/api/settings")
async def get_settings(request: Request):
    require_local_admin(request)
    load_dotenv(override=True)
    memory_enabled = os.getenv("CREW_MEMORY_ENABLED", "true").lower() in (
        "true",
        "1",
        "yes",
    )
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY", "")
    )
    model_name = (
        os.getenv("MODEL_NAME")
        or "gemini/gemini-3.7-flash"
    )
    return {
        "api_key_configured": bool(api_key),
        "model_name": model_name,
        "provider": "google-ai-studio",
        "memory_enabled": memory_enabled,
        "embedder_provider": os.getenv("EMBEDDER_PROVIDER", "onnx"),
    }


@app.post("/api/settings")
async def save_settings(req: SettingsRequest, request: Request):
    require_local_admin(request)
    memory_str = "true" if req.memory_enabled else "false"

    env_content = (
        f"# Google AI Studio / Gemini API Configuration\n"
        f"GEMINI_API_KEY={req.api_key}\n"
        f"GOOGLE_API_KEY={req.api_key}\n"
        f"MODEL_NAME={req.model_name}\n\n"
        f"# CrewAI Contextual Memory Configuration\n"
        f"CREW_MEMORY_ENABLED={memory_str}\n"
        f"EMBEDDER_PROVIDER={req.embedder_provider}\n"
    )
    os.environ["GEMINI_API_KEY"] = req.api_key
    os.environ["GOOGLE_API_KEY"] = req.api_key
    os.environ["MODEL_NAME"] = req.model_name

    ENV_FILE.write_text(env_content, encoding="utf-8")
    os.environ["CREW_MEMORY_ENABLED"] = memory_str
    os.environ["EMBEDDER_PROVIDER"] = req.embedder_provider
    return {"status": "ok"}


@app.get("/api/memory/status")
async def memory_status():
    load_dotenv(override=True)
    memory_active = os.getenv("CREW_MEMORY_ENABLED", "true").lower() in (
        "true",
        "1",
        "yes",
    )
    embedder_choice = os.getenv("EMBEDDER_PROVIDER", "onnx")
    return {
        "memory_enabled": memory_active,
        "embedder_provider": embedder_choice,
        "architecture": "Unified Multi-Tier (Short-Term, Long-Term & Entity Memory)",
        "storage": "LanceDB Persistent Vector Store",
        "agents": [
            "1. YouTube Content Researcher",
            "2. Benchmark & Web Cross-Verifier",
            "3. Senior Master Writer",
            "4. Visual Architecture Diagrammer",
            "5. Code QA Inspector",
            "6. Editor-in-Chief",
            "7. SEO Growth Strategist",
            "8. Podcast Audio Producer",
            "9. Newsletter Strategist",
        ],
    }


@app.post("/api/memory/reset")
async def reset_memory_endpoint():
    from crew import reset_crew_memory

    success = reset_crew_memory()
    return {
        "status": "ok" if success else "cleared",
        "message": "Crew persistent memory reset successfully.",
    }


class YouTubeSearchRequest(BaseModel):
    query: str
    max_videos: int = 3


@app.post("/api/youtube/search")
async def api_search_youtube(req: YouTubeSearchRequest):
    from tools import query_youtube_database

    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: query_youtube_database(q, max_videos=req.max_videos)
    )
    return result


class TrainRequest(BaseModel):
    iterations: int = 2
    filename: str = "trained_agents.pkl"
    topic: str = "AI vs ML vs Data Science"
    channel: str = "@krishnaik06"


@app.post("/api/train")
async def train_endpoint(req: TrainRequest):
    from crew import train

    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None,
            lambda: train(
                n_iterations=req.iterations,
                filename=req.filename,
                topic=req.topic,
                channel=req.channel,
            ),
        )
        return {
            "status": "ok",
            "message": f"Successfully trained 9 agents for {req.iterations} iterations! Saved weights to {req.filename}",
            "iterations": req.iterations,
            "filename": req.filename,
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err



@app.post("/api/generate-cover")
async def generate_cover_endpoint(req: CoverGenerateRequest):
    from image_gen import generate_cover_banner

    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    result = generate_cover_banner(
        topic=topic,
        channel=req.channel,
        style_key=req.style_key,
    )
    return result


@app.get("/api/latest-cover")
async def get_latest_cover():
    latest_img = STATIC_DIR / "latest_cover.jpg"
    if latest_img.exists():
        return {
            "image_url": "/static/latest_cover.jpg",
            "exists": True,
        }
    return {"exists": False, "image_url": None}


@app.post("/api/publish-webhook")
async def publish_webhook(req: WebhookPublishRequest, request: Request):
    require_local_admin(request)
    url = safe_webhook_url(req.webhook_url)

    payload = {
        "event": "crewai.studio.master_package.published",
        "topic": req.topic,
        "channel": req.channel,
        "article_markdown": req.markdown_content,
        "social_snippets": req.social_content,
        "podcast_script": req.podcast_content,
        "newsletter": req.newsletter_content,
        "source": "CrewAI 9-Agent Master Studio Engine",
    }

    def _send_payload():
        data = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CrewAI-Studio-Publisher/3.5",
            },
            method="POST",
        )
        with post_json(url, payload, timeout=15) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8", errors="replace")
            return status_code, body[:500]

    try:
        status_code, body = await asyncio.to_thread(_send_payload)
        return {"status": "ok", "http_status": status_code, "response": body}
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        TimeoutError,
        ValueError,
    ) as err:
        raise HTTPException(
            status_code=502, detail=f"Webhook dispatch failed: {err!s}"
        ) from err


@app.post("/api/export-html")
async def export_html(req: HtmlExportRequest, request: Request):
    require_local_admin(request)
    # The exported body is intentionally treated as HTML. This endpoint is local-only in the
    # production profile; callers should sanitize untrusted content before publishing it.
    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req.topic} • AI Published Master Article</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
    <style>
        :root {{
            --bg: #0d1117;
            --text: #c9d1d9;
            --heading: #58a6ff;
            --accent: #79c0ff;
            --border: #30363d;
            --code-bg: #161b22;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            line-height: 1.7;
            max-width: 860px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        h1, h2, h3, h4 {{
            color: var(--heading);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 700;
        }}
        h1 {{ font-size: 2.2rem; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
        h2 {{ font-size: 1.6rem; border-bottom: 1px solid rgba(48,54,61,0.5); padding-bottom: 8px; }}
        p, li {{ font-size: 1.05rem; margin-bottom: 1rem; }}
        ul, ol {{ padding-left: 24px; margin-bottom: 1rem; }}
        blockquote {{
            border-left: 4px solid var(--heading);
            padding: 8px 16px;
            margin: 1.5rem 0;
            background: rgba(88, 166, 255, 0.08);
            border-radius: 0 8px 8px 0;
        }}
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.92rem;
        }}
        code:not(pre code) {{
            background: rgba(110, 118, 129, 0.4);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 10px 14px;
            text-align: left;
        }}
        th {{ background: var(--code-bg); color: var(--accent); }}
        .watermark {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            font-size: 0.85rem;
            color: #8b949e;
            text-align: center;
        }}
    </style>
</head>
<body>
    <article>
        {req.html_body}
    </article>
    <footer class="watermark">
        Generated autonomously by CrewAI 9-Agent Master Studio • Powered by Google AI Studio Gemini API
    </footer>
</body>
</html>"""
    return Response(
        content=styled_html,
        media_type="text/html",
        headers={
            "Content-Disposition": (
                f"attachment; filename=blog-{req.topic.lower().replace(' ', '-')[:30]}.html"
            )
        },
    )


@app.post("/api/generate")
async def generate_blog(req: GenerateRequest):
    """Backward-compatible generation endpoint.

    New clients should use POST /api/jobs and poll /api/jobs/{job_id}.
    """
    from jobs import create_job, get_job

    job = create_job(req.topic.strip(), req.channel.strip() or "@krishnaik06")
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "status_url": f"/api/jobs/{job['job_id']}",
        "events_url": f"/api/jobs/{job['job_id']}/events",
    }


@app.post("/api/jobs")
async def create_generation_job(req: GenerateRequest):
    from jobs import create_job
    return create_job(req.topic.strip(), req.channel.strip() or "@krishnaik06")


@app.get("/api/jobs/{job_id}")
async def get_generation_job(job_id: str):
    from jobs import get_job
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs/{job_id}/events")
async def stream_generation_events(job_id: str):
    from jobs import event_stream
    if not await event_stream.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return StreamingResponse(event_stream.iter(job_id), media_type="text/event-stream")


@app.get("/api/jobs/{job_id}/artifacts")
async def get_generation_artifacts(job_id: str):
    from jobs import get_job
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "artifacts": job.get("artifacts", {})}

