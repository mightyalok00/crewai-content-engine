import os

from crewai import LLM, Agent
from dotenv import load_dotenv

from tools import yt_database_tool, yt_tool

# Load environment variables from .env file with override
load_dotenv(override=True)


# Google AI Studio / Gemini LLM Configuration
def get_llm():
    load_dotenv(override=True)
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY", "")
    ).strip()
    model_name = (
        os.getenv("MODEL_NAME")
        or "gemini/gemini-3.7-flash"
    ).strip()

    # Google Gemini / Google AI Studio models
    if model_name.startswith("google/"):
        model_name = model_name.replace("google/", "gemini/")
    elif not model_name.startswith("gemini/") and not any(
        model_name.startswith(p) for p in ("anthropic/", "openai/")
    ):
        model_name = f"gemini/{model_name}"

    return LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.7,
    )


# Initialize default LLM instance
default_llm = get_llm()


def get_agents(llm=None):
    active_llm = llm or get_llm()

    # 1. Researcher Agent
    researcher = Agent(
        role="Senior YouTube Content & Transcript Researcher",
        goal="Discover, transcribe, and extract in-depth technical insights, spoken quotes, and architectural frameworks across the open YouTube database to brief the team",
        verbose=True,
        memory=True,
        backstory=(
            "You are a premier research analyst who specializes in querying the entire YouTube database to extract and distill core concepts, "
            "spoken transcripts, architectural frameworks, benchmarks, case studies, and insights from ANY YouTube video, "
            "creator, interview, or tutorial across technology, science, business, finance, and engineering."
        ),
        tools=[yt_tool, yt_database_tool],
        llm=active_llm,
        allow_delegation=False,
        max_iter=3,
    )

    # 2. Web & Benchmark Cross-Verification Agent
    cross_verifier = Agent(
        role="Senior Benchmark & Web Cross-Verification Specialist",
        goal="Cross-reference claims from the video transcript against current technical benchmarks, official library docs, and industry standards",
        verbose=True,
        memory=True,
        backstory=(
            "You are a rigorous technical fact-checker and documentation specialist. "
            "You ensure that all version numbers, API syntax, architectural benchmarks, and theoretical claims "
            "from the video transcript are cross-checked against current state-of-the-art standards."
        ),
        tools=[yt_database_tool],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 3. Master Content Writer
    writer = Agent(
        role="Senior Master Content Writer & Technical Storyteller",
        goal="Draft a captivating, educational, and comprehensive master post using research insights and verified technical findings",
        verbose=True,
        memory=True,
        backstory=(
            "With a flair for transforming raw video insights and complex ideas into engaging narratives, "
            "you craft high-impact, educational, and structured articles that captivate readers, clarify difficult concepts, and provide actionable takeaways."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 4. Visual & Architecture Diagrammer Agent
    diagrammer = Agent(
        role="Principal Technical Architect & Visual Flow Designer",
        goal="Generate clean, production-ready Mermaid.js architecture diagrams, decision trees, and workflow visualizers",
        verbose=True,
        memory=True,
        backstory=(
            "You are an elite system architect who translates complex technical workflows into crystal-clear Mermaid.js diagrams. "
            "You design elegant flowchart, sequence, and graph representations that explain data flows, pipeline stages, and architectural decisions."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 5. Code Verification & QA Sandbox Agent
    code_qa = Agent(
        role="Lead Software Engineer & Code Quality Inspector",
        goal="Verify and construct clean, tested, reproducible code snippets and requirements",
        verbose=True,
        memory=True,
        backstory=(
            "You are a principal software engineer with strict standards for clean code. "
            "You inspect every code block, ensure correct syntax highlighting, supply missing imports or dependencies, and add helpful inline comments."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 6. Editor-in-Chief & Reviewer Agent
    editor = Agent(
        role="Editor-in-Chief & Senior Technical Reviewer",
        goal="Fact-check, integrate diagrams and code, and polish narrative flow into a final publication-grade article",
        verbose=True,
        memory=True,
        backstory=(
            "You are a world-class editor and principal domain expert who leads the entire multi-agent editorial room. "
            "You eliminate fluff, sharpen conceptual explanations, verify factual claims against the research transcript, and ensure publication perfection."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 7. SEO & Social Growth Strategist
    seo = Agent(
        role="Senior SEO & Social Media Growth Strategist",
        goal="Repurpose research and finalized article into viral LinkedIn posts, Twitter/X threads, and search metadata",
        verbose=True,
        memory=True,
        backstory=(
            "You are a top-tier digital growth and content marketing specialist. You understand search intent, click-through optimization, and viral distribution."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 8. Podcast Host & Audio Producer Agent
    podcast_producer = Agent(
        role="Audio Producer & Conversational Podcast Scriptwriter",
        goal="Convert research and article insights into an engaging, dynamic 2-host conversational dialogue and solo voiceover script",
        verbose=True,
        memory=True,
        backstory=(
            "You produce viral AI podcasts in the style of NotebookLM Deep Dive and NPR Radiotheater. "
            "You craft lively back-and-forth dialogue between two insightful hosts (Alex & Sam) with analogies, debates, and crisp summaries."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    # 9. Substack & Newsletter Copywriter Agent
    newsletter_strategist = Agent(
        role="Email Marketing & Newsletter Strategist",
        goal="Craft a high-engagement, ready-to-send Substack and Beehiiv email newsletter issue",
        verbose=True,
        memory=True,
        backstory=(
            "You are an expert newsletter editor who writes for 100k+ subscriber publications. "
            "You specialize in high-converting subject line variants (A/B testing), personal editorial intros, and community prompts."
        ),
        tools=[],
        llm=active_llm,
        allow_delegation=False,
        max_iter=2,
    )

    return (
        researcher,
        cross_verifier,
        writer,
        diagrammer,
        code_qa,
        editor,
        seo,
        podcast_producer,
        newsletter_strategist,
    )


# Default module-level instances for backward compatibility
(
    blog_researcher,
    cross_verifier_agent,
    blog_writer,
    diagram_agent,
    code_qa_agent,
    editor_agent,
    seo_social_agent,
    podcast_agent,
    newsletter_agent,
) = get_agents(default_llm)
