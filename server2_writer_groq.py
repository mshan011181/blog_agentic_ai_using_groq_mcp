"""
MCP SERVER 2: WRITER AGENT (Groq Edition)
==========================================
Role: Takes research JSON -> generates full blog post HTML using Groq API
Models: llama-3.3-70b-versatile (high quality writing, ~500 TPS on Groq)
Compatible with MCP 1.26.0+
"""

import json
import sys
import os
from groq import Groq
from mcp.server.fastmcp import FastMCP

if sys.platform == "win32":
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

mcp = FastMCP("blog-writer")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
WRITER_MODEL = os.environ.get("GROQ_WRITER_MODEL", "llama-3.3-70b-versatile")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def call_groq(prompt: str, system: str = "", model: str = WRITER_MODEL) -> str:
    """Call Groq API and return generated text."""
    if not groq_client:
        return "ERROR: GROQ_API_KEY not set"
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or "You are an expert technical blog writer."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Groq error: {e}"


@mcp.tool()
def generate_blog_outline(research_json: str, post_type: str = "tutorial") -> str:
    """Generate a structured blog post outline from research data."""
    try:
        research = json.loads(research_json)
    except Exception:
        research = {"topic": research_json, "target_audience": "developers",
                    "wikipedia_summary": "", "trending_stories": []}

    prompt = f"""Create a detailed blog post outline for a {post_type} article.

TOPIC: {research.get('topic', '')}
TARGET AUDIENCE: {research.get('target_audience', 'developers')}

BACKGROUND SUMMARY:
{research.get('wikipedia_summary', '')[:800]}

TRENDING CONTEXT:
{json.dumps(research.get('trending_stories', [])[:3], indent=2)}

Create an outline with:
1. Compelling H1 title
2. Introduction hook (2-3 sentences)
3. 4-6 main sections with H2 headings
4. Key points for each section (bullet list)
5. Practical code example section
6. Conclusion with call-to-action

Format as structured JSON with keys: title, introduction, sections (array), conclusion"""

    return call_groq(prompt,
        system="You are a technical blog strategist for shanmaha.com, a blog about AI and Oracle DBA topics.")


@mcp.tool()
def generate_blog_content(
    topic: str,
    outline: str,
    research_json: str,
    tone: str = "technical",
    word_count: int = 1200
) -> str:
    """Write the full blog post in HTML using Groq based on the outline."""
    try:
        research = json.loads(research_json)
        audience = research.get('target_audience', 'developers')
    except Exception:
        audience = "developers"

    prompt = f"""Write a complete blog post in HTML format.

TOPIC: {topic}
TONE: {tone}
TARGET WORD COUNT: {word_count} words
OUTLINE:
{outline}

RESEARCH DATA:
{research_json[:1500]}

REQUIREMENTS:
- Use proper HTML structure: <article>, <h1>, <h2>, <h3>, <p>, <code>, <pre>, <ul>, <ol>
- Include at least one practical code block with real, runnable examples
- Add callout boxes using <div class="callout"> for important notes
- Write for {audience}
- Make it practical and hands-on, not just theory

Output ONLY the HTML article body (no <html> or <body> tags), starting with <article>"""

    return call_groq(prompt,
        system="You are an expert technical writer for shanmaha.com. Write clear, practical, SEO-optimized blog posts.")


@mcp.tool()
def generate_seo_metadata(topic: str, blog_content: str, target_keywords: list = None) -> str:
    """Generate SEO metadata: title, meta description, tags, and slug."""
    keywords = target_keywords or []
    prompt = f"""Generate SEO metadata for this blog post. Output ONLY valid JSON, no markdown fences.

TOPIC: {topic}
CONTENT PREVIEW: {blog_content[:800]}
TARGET KEYWORDS: {', '.join(keywords) if keywords else 'auto-detect from content'}

Return JSON with these exact keys:
{{
  "seo_title": "60-character max title with primary keyword",
  "meta_description": "155-character max compelling description",
  "slug": "url-friendly-slug-with-hyphens",
  "primary_keyword": "main keyword",
  "secondary_keywords": ["kw1", "kw2", "kw3"],
  "tags": ["tag1", "tag2", "tag3"],
  "reading_time_minutes": 5,
  "category": "AI / Oracle / DevOps"
}}"""

    return call_groq(prompt,
        system="You are an SEO specialist. Output only valid JSON, no extra text, no markdown fences.")


@mcp.tool()
def package_for_publisher(
    topic: str,
    html_content: str,
    seo_metadata: str,
    research_sources: list = None
) -> str:
    """Bundle blog post + metadata into final JSON for Publisher agent."""
    try:
        seo = json.loads(seo_metadata)
    except Exception:
        # Strip markdown fences if Groq wrapped JSON in ```
        cleaned = seo_metadata.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        try:
            seo = json.loads(cleaned.strip())
        except Exception:
            seo = {"raw": seo_metadata, "slug": "blog-post", "tags": [],
                   "seo_title": topic, "meta_description": ""}

    return json.dumps({
        "status":           "ready_to_publish",
        "topic":            topic,
        "seo":              seo,
        "html_content":     html_content,
        "sources":          research_sources or [],
        "pipeline_version": "v2.0-groq",
        "blog":             "shanmaha.com"
    }, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
