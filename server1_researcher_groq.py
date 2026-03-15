"""
MCP SERVER 1: RESEARCH AGENT (Groq Edition)
=============================================
Role: Fetches topic data from free APIs — Wikipedia, HackerNews, DEV.to
No Groq calls here — pure data fetching, no LLM needed
Compatible with MCP 1.26.0+
"""

import json
import sys
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

if sys.platform == "win32":
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

mcp = FastMCP("blog-researcher")


def fetch_url(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BlogPipelineBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_wikipedia(topic: str) -> str:
    """Get a Wikipedia summary for any topic."""
    encoded = urllib.parse.quote(topic.replace(" ", "_"))
    data = fetch_url(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}")
    if "error" in data:
        return f"Wikipedia error: {data['error']}"
    return json.dumps({
        "title":   data.get("title", ""),
        "summary": data.get("extract", "")[:1500],
        "url":     data.get("content_urls", {}).get("desktop", {}).get("page", "")
    }, indent=2)


@mcp.tool()
def get_hackernews_top(limit: int = 5) -> str:
    """Get top trending tech stories from Hacker News."""
    limit   = min(limit, 10)
    ids     = fetch_url("https://hacker-news.firebaseio.com/v0/topstories.json")
    stories = []
    if isinstance(ids, list):
        for sid in ids[:limit]:
            s = fetch_url(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
            if isinstance(s, dict) and "title" in s:
                stories.append({"title": s.get("title"), "url": s.get("url", ""),
                                 "score": s.get("score", 0), "comments": s.get("descendants", 0)})
    return json.dumps(stories, indent=2)


@mcp.tool()
def get_devto_articles(tag: str, limit: int = 5) -> str:
    """Get recent blog posts from DEV.to for a given tag."""
    data = fetch_url(f"https://dev.to/api/articles?tag={tag}&per_page={limit}&top=7")
    if isinstance(data, list):
        return json.dumps([{
            "title":        a.get("title"),
            "description":  a.get("description", "")[:200],
            "url":          a.get("url"),
            "reactions":    a.get("positive_reactions_count", 0),
            "reading_time": a.get("reading_time_minutes", 0)
        } for a in data], indent=2)
    return f"DEV.to error: {data}"


@mcp.tool()
def compile_research(
    topic: str,
    wikipedia_summary: str,
    trending_stories: list,
    related_articles: list = None,
    target_audience: str = "AI/tech developers"
) -> str:
    """Compile all gathered research into a structured JSON blob for the Writer agent."""
    return json.dumps({
        "status":           "research_complete",
        "topic":            topic,
        "target_audience":  target_audience,
        "wikipedia_summary": wikipedia_summary,
        "trending_stories": trending_stories,
        "related_articles": related_articles or [],
        "instructions_for_writer": (
            "Use this research to write a detailed, practical blog post. "
            "Focus on hands-on examples. Target audience: " + target_audience
        )
    }, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
