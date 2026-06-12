import json
import feedparser
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("BlogFetcher")

@mcp.tool()
def fetch_rss_feeds(url: str, limit: int = 5) -> str:
    """
    Fetches the latest articles from an RSS/Atom feed.
    
    Args:
        url: The URL of the RSS or Atom feed.
        limit: The maximum number of articles to fetch.
        
    Returns:
        A JSON string containing a list of articles with their title, link, and content/summary.
    """
    try:
        feed = feedparser.parse(url)
        
        if feed.bozo:
            return json.dumps({"error": f"Failed to parse feed: {feed.bozo_exception}"})
            
        articles = []
        for entry in feed.entries[:limit]:
            # Try to get the fullest content available
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
                
            articles.append({
                "title": entry.title if hasattr(entry, "title") else "Untitled",
                "link": entry.link if hasattr(entry, "link") else url,
                "content": content
            })
            
        return json.dumps({
            "feed_title": feed.feed.title if hasattr(feed.feed, "title") else "Unknown Feed",
            "articles": articles
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Start the MCP server using stdio
    mcp.run(transport='stdio')
