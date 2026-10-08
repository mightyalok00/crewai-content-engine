import os
import sys

# Configure UTF-8 encoding for standard output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv(override=True)

from crewai import Crew, Process

from agents import (
    blog_researcher,
    cross_verifier_agent,
    blog_writer,
    diagram_agent,
    code_qa_agent,
    editor_agent,
    seo_social_agent,
    podcast_agent,
    newsletter_agent,
)
from tasks import (
    research_task,
    cross_verify_task,
    write_task,
    diagram_task,
    code_qa_task,
    review_and_edit_task,
    seo_social_task,
    podcast_script_task,
    newsletter_task,
)


def get_embedder_config() -> dict:
    """Configure smart multi-tier embedding provider for agent memory.

    Defaults to fast, zero-cost local ONNX MiniLM embeddings (no API credits required),
    or uses OpenAI / Google embeddings if explicitly configured in environment.
    """
    provider = os.getenv("EMBEDDER_PROVIDER", "onnx").lower().strip()

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return {
            "provider": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model_name": os.getenv(
                    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
                ),
            },
        }
    elif provider == "google" and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return {
            "provider": "google",
            "config": {
                "api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
                "model_name": os.getenv("GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004"),
            },
        }
    else:
        # Default local zero-cost embedding via ONNX (no external API calls, highly reliable)
        return {"provider": "onnx"}


def configure_output_directory(output_dir: str | os.PathLike[str]) -> None:
    """Route CrewAI file-producing tasks to an isolated job directory."""
    output_path = os.fspath(output_dir)
    os.makedirs(output_path, exist_ok=True)
    review_and_edit_task.output_file = os.path.join(output_path, "new_blog_post.md")
    seo_social_task.output_file = os.path.join(output_path, "social_snippets.md")
    podcast_script_task.output_file = os.path.join(output_path, "podcast_script.md")
    newsletter_task.output_file = os.path.join(output_path, "newsletter.md")


def create_blog_crew(memory_enabled: bool | None = None) -> Crew:
    """Instantiate the 9-Agent Master Studio Crew with full contextual memory support."""
    load_dotenv(override=True)

    if memory_enabled is None:
        is_memory_active = os.getenv("CREW_MEMORY_ENABLED", "true").lower() in (
            "true",
            "1",
            "yes",
        )
    else:
        is_memory_active = memory_enabled

    embedder_cfg = get_embedder_config() if is_memory_active else None

    agents = [
        blog_researcher,
        cross_verifier_agent,
        blog_writer,
        diagram_agent,
        code_qa_agent,
        editor_agent,
        seo_social_agent,
        podcast_agent,
        newsletter_agent,
    ]

    tasks = [
        research_task,
        cross_verify_task,
        write_task,
        diagram_task,
        code_qa_task,
        review_and_edit_task,
        seo_social_task,
        podcast_script_task,
        newsletter_task,
    ]

    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        memory=is_memory_active,
        embedder=embedder_cfg,
        cache=True,
        max_rpm=10,
        share_crew=True,
        verbose=True,
    )


# Default module instance for direct kickoff or backward compatibility
blog_crew = create_blog_crew()


def reset_crew_memory() -> bool:
    """Reset and clear persistent crew memories."""
    try:
        from crewai.memory.unified_memory import Memory

        # Attempt to reset unified memory if initialized
        Memory().reset_all()
        return True
    except Exception:
        return False


def run(topic: str = "AI vs ML vs Data Science", channel: str = "@krishnaik06"):
    print("\n" + "=" * 60)
    print("🎬 Kicking off 9-Agent Master Studio Pipeline...")
    print(f"   Topic:   {topic}")
    print(f"   Channel: {channel}")
    print("=" * 60 + "\n")

    inputs = {"topic": topic, "channel": channel}
    crew_instance = create_blog_crew()
    result = crew_instance.kickoff(inputs=inputs)

    print("\n" + "=" * 60)
    print("✨ 9-Agent Studio Execution Finished Successfully!")
    print("=" * 60)
    return result


def train(
    n_iterations: int = 2,
    filename: str = "trained_agents.pkl",
    topic: str = "AI vs ML vs Data Science",
    channel: str = "@krishnaik06",
):
    """Train the 9-Agent Crew for a specified number of iterations.

    This optimizes agent prompt execution and saves weights/state to a pickle file.
    """
    print("\n" + "=" * 60)
    print(f"🏋️ Starting 9-Agent Crew Training ({n_iterations} iterations)...")
    print(f"   Topic:    {topic}")
    print(f"   Channel:  {channel}")
    print(f"   Artifact: {filename}")
    print("=" * 60 + "\n")

    inputs = {"topic": topic, "channel": channel}
    crew_instance = create_blog_crew()
    crew_instance.train(n_iterations=n_iterations, filename=filename, inputs=inputs)

    print("\n" + "=" * 60)
    print(f"🎉 Training Complete! Trained agent artifact saved to: {filename}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run()

