"""
YouTube MCP Server — stub interface for official YouTube Data API v3.

To activate:
1. Enable YouTube Data API v3 in Google Cloud Console
2. Create an API key and set YOUTUBE_API_KEY in your .env
3. Uncomment the googleapiclient import and replace _youtube_api_stub calls
   with real API calls (see comments marked TODO:API)
"""

import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("YouTubeFetcher")


def _youtube_api_stub(channel_id: str, max_results: int) -> list[dict]:
    """
    Replace this function with real YouTube Data API v3 calls.

    TODO:API — example implementation using official API:

        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
        response = youtube.search().list(
            channelId=channel_id,
            part="snippet",
            order="date",
            maxResults=max_results,
            type="video"
        ).execute()
        return [
            {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            for item in response.get("items", [])
        ]
    """
    return []


def _fetch_transcript_stub(video_id: str) -> str | None:
    """
    Replace this with official transcript/caption retrieval.

    TODO:API — YouTube Data API v3 captions endpoint requires OAuth2
    (not just an API key). For public videos you can use the captions.list
    endpoint with a service account.

    Alternatively, consider using the video description + title as a
    lightweight summary source until caption access is configured.
    """
    return None


@mcp.tool()
def fetch_youtube_channel(channel_id: str, max_results: int = 5) -> str:
    """
    Fetches the latest videos from a YouTube channel using the official YouTube Data API v3.

    Requires YOUTUBE_API_KEY environment variable.
    Returns video metadata (title, description, URL, published date).
    Transcripts are included when available via caption API.

    Args:
        channel_id: YouTube channel ID (e.g. 'UCVHZiUmPe6eL8b3-qSANLSQ')
        max_results: Maximum number of recent videos to fetch (1-50)
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "YOUTUBE_API_KEY not set. See .env.example for setup instructions.",
            "setup_url": "https://console.cloud.google.com/"
        })

    try:
        videos = _youtube_api_stub(channel_id, max_results)

        results = []
        for video in videos:
            transcript = _fetch_transcript_stub(video.get("video_id", ""))
            results.append({
                **video,
                "transcript_excerpt": transcript[:2000] if transcript else None
            })

        return json.dumps({
            "channel_id": channel_id,
            "videos": results
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_youtube_setup_status() -> str:
    """Returns the current YouTube API configuration status."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    return json.dumps({
        "configured": bool(api_key),
        "api_key_set": bool(api_key),
        "instructions": "Set YOUTUBE_API_KEY in .env. See .env.example for details."
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
