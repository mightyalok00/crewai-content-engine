from crewai import Task

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
from tools import yt_database_tool, yt_tool

# Task 1: Research Task (Universal YouTube & Transcript extraction)
research_task = Task(
    description=(
        "1. Query the open YouTube database to examine the target video, topic, or channel:\n"
        "   - Target Topic/Video: '{topic}'\n"
        "   - Target Channel/URL: '{channel}'\n"
        "2. Extract spoken transcripts across top matching videos, core insights, explanations, comparisons, and actionable takeaways.\n"
        "3. Provide a structured, high-fidelity research brief with exact quotes, terminology, definitions, and code/framework details.\n"
        "4. **Inter-Agent Collaboration**: Be ready to answer questions and provide exact transcript snippets when teammates ask."
    ),
    expected_output=(
        "A comprehensive research brief summarizing the video title, author/channel, core concepts, "
        "spoken transcript highlights, and structured takeaways."
    ),
    tools=[yt_tool, yt_database_tool],
    agent=blog_researcher,
)

# Task 2: Cross-Source Benchmark & Technical Fact Verification
cross_verify_task = Task(
    description=(
        "1. Review the initial research brief from the Researcher on topic '{topic}'.\n"
        "2. Query the YouTube database and documentation to verify technical claims, software library versions, API signatures, and benchmark numbers against modern industry standards.\n"
        "3. **Inter-Agent Dialogue**: Confer with the Researcher or Writer if any transcript claims appear ambiguous, dated, or need caveats.\n"
        "4. Supply verified architectural references and benchmark tables to enrich the draft."
    ),
    expected_output=(
        "A technical verification report highlighting confirmed facts, package version notes, caveats, and supplementary benchmarks."
    ),
    tools=[yt_database_tool],
    agent=cross_verifier_agent,
    context=[research_task],
)

# Task 3: Writing Task (Drafting the Master Post)
write_task = Task(
    description=(
        "1. Review the verified research brief on topic '{topic}' ({channel}).\n"
        "2. **Inter-Agent Dialogue**: If you need additional quotes, timestamps, or benchmark clarification, delegate questions to the Researcher or Verifier.\n"
        "3. Transform the core ideas into an engaging, authoritative, and deeply informative master blog post.\n"
        "4. Include a captivating H1 title, clear structured H2/H3 sections, conceptual breakdown, real-world examples, and an actionable conclusion.\n"
        "5. Output the complete draft in clean GitHub-flavored Markdown."
    ),
    expected_output=(
        "A comprehensive first-draft Markdown blog post based on the researched video content."
    ),
    tools=[],
    agent=blog_writer,
    context=[research_task, cross_verify_task],
)

# Task 4: Visual Architecture & Diagram Design
diagram_task = Task(
    description=(
        "1. Analyze the drafted article for '{topic}'.\n"
        "2. **Inter-Agent Dialogue**: Coordinate with the Writer to identify the key architectural workflows and mental models that need visualization.\n"
        "3. Design 2-3 production-ready, beautiful Mermaid.js diagrams (flowchart, sequence diagram, or system architecture graph).\n"
        "4. Ensure the Mermaid syntax is 100% valid with quoted node labels and clear directional arrows (`-->`)."
    ),
    expected_output=(
        "A collection of validated Mermaid.js diagram code snippets complete with explanatory captions."
    ),
    tools=[],
    agent=diagram_agent,
    context=[write_task],
)

# Task 5: Code Quality & Sandbox Verification
code_qa_task = Task(
    description=(
        "1. Inspect all code blocks and technical commands in the draft for '{topic}'.\n"
        "2. **Inter-Agent Dialogue**: Ask the Writer or Verifier for context on specific library dependencies, data formats, or frameworks.\n"
        "3. Ensure all required library imports, type annotations, and defensive error handling are included.\n"
        "4. Add informative inline comments and format code cleanly with language identifiers (e.g., ```python, ```bash)."
    ),
    expected_output=(
        "A verified suite of tested, clean, production-grade code snippets ready to be embedded into the master post."
    ),
    tools=[],
    agent=code_qa_agent,
    context=[write_task, diagram_task],
)

# Task 6: Editorial Fact-Checking & Final Master Article Synthesis
review_and_edit_task = Task(
    description=(
        "1. Lead the editorial review room for '{topic}'.\n"
        "2. **Inter-Agent Dialogue & Delegation**: If any section lacks depth, clarity, or code accuracy, delegate refinement requests back to the Writer, Verifier, or Code QA agent.\n"
        "3. **Fact-Checking**: Ensure statements, quotes, frameworks, and explanations accurately reflect the video content.\n"
        "4. **Visual & Code Integration**: Embed the Mermaid diagrams and verified code blocks cleanly into the appropriate sections.\n"
        "5. **Editorial Polish**: Maximize readability, eliminate fluff, add informative callout blockquotes (`> [!NOTE]` or `> [!TIP]`), create comparison tables where helpful, and ensure clean H1/H2/H3 formatting.\n"
        "6. Output the final, publish-ready master article in GitHub-flavored Markdown."
    ),
    expected_output=(
        "A verified, fact-checked, code-reviewed, diagram-enhanced, and polished master Markdown blog post ready for immediate publication."
    ),
    tools=[],
    agent=editor_agent,
    context=[research_task, cross_verify_task, write_task, diagram_task, code_qa_task],
    output_file="new_blog_post.md",
)

# Task 7: SEO & Viral Social Media Distribution Kit
seo_social_task = Task(
    description=(
        "1. Read the final approved master blog post for '{topic}'.\n"
        "2. **Inter-Agent Dialogue**: Consult the Editor on the top 3 standout insights to feature in social hooks.\n"
        "3. Generate an SEO Growth & Social Distribution Kit containing:\n"
        "   - **SEO Metadata**: Meta Title (under 60 chars), Meta Description (under 160 chars), 10 high-intent keyword tags, and URL slug.\n"
        "   - **LinkedIn Authority Post**: Compelling hook, 5 key value-packed takeaways with emojis, discussion prompt, and targeted hashtags.\n"
        "   - **Twitter/X Thread (4-5 Tweets)**: Punchy opening hook, insight breakdown, framework tweet, and CTA.\n"
        "   - **Executive Summary**: 30-second bulleted TL;DR.\n"
        "4. Format cleanly in GitHub-flavored Markdown."
    ),
    expected_output=(
        "A complete, ready-to-post SEO and Multi-Platform Social Media Growth Kit in Markdown."
    ),
    tools=[],
    agent=seo_social_agent,
    context=[review_and_edit_task],
    output_file="social_snippets.md",
)

# Task 8: Conversational Audio Podcast / Voiceover Script
podcast_script_task = Task(
    description=(
        "1. Read the final approved master post for '{topic}'.\n"
        "2. **Inter-Agent Dialogue**: Confer with the Writer and SEO Strategist on the most relatable analogies and high-converting episode hooks.\n"
        "3. Create a dynamic 2-host conversational podcast script (Hosts: Alex & Sam) inspired by NotebookLM Deep Dive:\n"
        "   - **Intro (30s)**: High-energy teaser and hook.\n"
        "   - **Deep Dive (3-5 mins)**: Engaging back-and-forth dialogue explaining core mechanisms with relatable metaphors.\n"
        "   - **Host Debates & Questions**: Thought-provoking perspectives on future implications.\n"
        "   - **Outro (30s)**: Key takeaway and sign-off.\n"
        "4. Also include a crisp **60-Second Solo Executive Voiceover Summary** at the bottom.\n"
        "5. Output cleanly in GitHub-flavored Markdown."
    ),
    expected_output=(
        "A full 2-host conversational audio podcast script and solo executive voiceover narration in Markdown."
    ),
    tools=[],
    agent=podcast_agent,
    context=[review_and_edit_task],
    output_file="podcast_script.md",
)

# Task 9: Substack & Beehiiv Newsletter Issue
newsletter_task = Task(
    description=(
        "1. Read the finalized master post and social growth kit for '{topic}'.\n"
        "2. **Inter-Agent Dialogue**: Coordinate with the SEO Strategist and Diagrammer on top-performing hooks and visual diagrams to embed in the email.\n"
        "3. Craft a high-converting, publication-ready email newsletter issue formatted for Substack/Beehiiv:\n"
        "   - **3 A/B Test Subject Lines**: (Curiosity, Benefit-driven, Urgency).\n"
        "   - **Preview Text**: 1-sentence punchy teaser.\n"
        "   - **Personal Editorial Hook**: Warm, conversational greeting establishing why this topic matters today.\n"
        "   - **Core Story & Visual Breakdown**: Digestible breakdown with bullet points, callout takeaways, and action items.\n"
        "   - **Community Poll / Question**: Interactive sign-off prompt to drive email replies.\n"
        "4. Output cleanly in GitHub-flavored Markdown."
    ),
    expected_output=(
        "A complete, ready-to-send Substack/Beehiiv email newsletter draft in Markdown."
    ),
    tools=[],
    agent=newsletter_agent,
    context=[review_and_edit_task, seo_social_task],
    output_file="newsletter.md",
)
