"""
ORCHESTRATOR: Blog Pipeline Brain (Groq Edition)
=================================================
Run with:
  python orchestrator_groq.py "Model Context Protocol with Groq"

Requirements:
  pip install mcp groq
  Set GROQ_API_KEY environment variable
"""

import asyncio
import json
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq

# Fix Windows console Unicode encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ─── CONFIG ──────────────────────────────────────────────────────────────────
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
ORCHESTRATOR_MODEL = "llama-3.1-8b-instant"   # Fast decisions, cheap
WRITER_MODEL       = "llama-3.3-70b-versatile"         # Better quality writing
TARGET_AUDIENCE    = "Oracle DBA and AI engineer exploring agentic systems"
BLOG_NAME          = "shanmaha.com"
# ─────────────────────────────────────────────────────────────────────────────

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY environment variable not set.")
    print("  Set it with:  export GROQ_API_KEY='your_key_here'")
    sys.exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_server_params(script_name: str) -> StdioServerParameters:
    return StdioServerParameters(
        command="python",
        args=[os.path.join(BASE_DIR, script_name)],
        env={**os.environ}
    )


async def call_tool(session: ClientSession, server_name: str,
                    tool_name: str, arguments: dict) -> str:
    """Call a specific MCP tool directly — hardcoded sequence, no LLM routing."""
    print(f"\n  [{server_name}] -> Calling: {tool_name}")
    try:
        result = await session.call_tool(tool_name, arguments)
        output = result.content[0].text if result.content else ""
        print(f"  [{server_name}]   OK Got {len(output)} chars")
        return output
    except Exception as e:
        print(f"  [{server_name}]   ERROR: {e}")
        return ""


async def run_full_pipeline(topic: str):
    print(f"\n{'='*60}")
    print(f"  shanmaha.com Blog Auto-Pipeline (Groq Edition)")
    print(f"  Topic: {topic}")
    print(f"  Orchestrator: {ORCHESTRATOR_MODEL}")
    print(f"  Writer: {WRITER_MODEL}")
    print(f"{'='*60}\n")

    # ─── PHASE 1: RESEARCH ───────────────────────────────────────────
    print("\nPHASE 1: RESEARCH AGENT (Server 1)")
    print("-" * 40)

    async with stdio_client(get_server_params("server1_researcher_groq.py")) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            wiki_result = await call_tool(session, "Researcher", "search_wikipedia",
                                          {"topic": topic})

            hn_result = await call_tool(session, "Researcher", "get_hackernews_top",
                                        {"limit": 5})

            tag = topic.split()[0].lower()
            devto_result = await call_tool(session, "Researcher", "get_devto_articles",
                                           {"tag": tag, "limit": 5})

            wiki_data      = json.loads(wiki_result)   if wiki_result.startswith("{") else {}
            hn_stories     = json.loads(hn_result)     if hn_result.startswith("[")  else []
            devto_articles = json.loads(devto_result)  if devto_result.startswith("[") else []

            research_result = await call_tool(session, "Researcher", "compile_research", {
                "topic": topic,
                "wikipedia_summary": wiki_data.get("summary", wiki_result[:500]),
                "trending_stories":  [s.get("title", "") for s in hn_stories[:5]],
                "related_articles":  [a.get("title", "") for a in devto_articles[:5]],
                "target_audience":   TARGET_AUDIENCE
            })

    if not research_result:
        print("Research phase failed. Exiting.")
        return

    print(f"\n  Research complete ({len(research_result)} chars)")

    # ─── PHASE 2: WRITING ────────────────────────────────────────────
    print("\nPHASE 2: WRITER AGENT (Server 2)")
    print("-" * 40)

    async with stdio_client(get_server_params("server2_writer_groq.py")) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            outline_result = await call_tool(session, "Writer", "generate_blog_outline", {
                "research_json": research_result,
                "post_type": "tutorial"
            })

            content_result = await call_tool(session, "Writer", "generate_blog_content", {
                "topic":        topic,
                "outline":      outline_result,
                "research_json": research_result,
                "tone":         "technical",
                "word_count":   1200
            })

            seo_result = await call_tool(session, "Writer", "generate_seo_metadata", {
                "topic":           topic,
                "blog_content":    content_result,
                "target_keywords": ["groq", "mcp", "ai agents", "llm", "oracle dba"]
            })

            package_result = await call_tool(session, "Writer", "package_for_publisher", {
                "topic":            topic,
                "html_content":     content_result,
                "seo_metadata":     seo_result,
                "research_sources": [topic]
            })

    if not package_result:
        print("Writing phase failed. Exiting.")
        return

    print(f"\n  Writing complete ({len(package_result)} chars)")

    # ─── PHASE 3: PUBLISHING ─────────────────────────────────────────
    print("\nPHASE 3: PUBLISHER AGENT (Server 3)")
    print("-" * 40)

    async with stdio_client(get_server_params("server3_publisher_groq.py")) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            html_save_result = await call_tool(session, "Publisher", "save_local_html", {
                "package_json": package_result
            })

            wp_result = await call_tool(session, "Publisher", "generate_wordpress_export", {
                "package_json": package_result
            })

            html_file = json.loads(html_save_result).get("file", "") if html_save_result else ""
            wp_file   = json.loads(wp_result).get("file", "")        if wp_result        else ""

            await call_tool(session, "Publisher", "generate_pipeline_report", {
                "topic":          topic,
                "html_file":      html_file,
                "wordpress_file": wp_file,
                "seo_metadata":   seo_result
            })

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE!")
    output_dir = os.path.join(os.path.expanduser("~"), "blog-pipeline-output")
    print(f"  Output directory: {output_dir}")
    print(f"{'='*60}\n")

    if os.path.exists(output_dir):
        print("  Output files:")
        for f in sorted(os.listdir(output_dir)):
            fpath = os.path.join(output_dir, f)
            size  = os.path.getsize(fpath)
            print(f"    {f}  ({size:,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        topic = "How to use Groq with MCP to build AI agents"
    else:
        topic = " ".join(sys.argv[1:])

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(run_full_pipeline(topic))
