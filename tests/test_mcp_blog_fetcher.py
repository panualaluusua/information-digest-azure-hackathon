"""
Tests for the blog_fetcher MCP server tool logic.
Uses pytest-mock to avoid real HTTP calls.
"""

import json
import pytest
from unittest.mock import MagicMock, patch


# Import the tool function directly (without starting the MCP server)
from src.mcp_servers.blog_fetcher import fetch_rss_feeds


SAMPLE_ATOM_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Blog</title>
  <entry>
    <title>Great Article</title>
    <link href="https://testblog.example.com/great-article"/>
    <summary>A summary of the great article.</summary>
  </entry>
  <entry>
    <title>Another Post</title>
    <link href="https://testblog.example.com/another-post"/>
    <content type="html">&lt;p&gt;Full content here.&lt;/p&gt;</content>
  </entry>
</feed>"""

SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>RSS Test Feed</title>
    <item>
      <title>RSS Item One</title>
      <link>https://rss.example.com/item-1</link>
      <description>Description of item one.</description>
    </item>
  </channel>
</rss>"""


class TestFetchRssFeeds:
    def test_returns_articles_from_valid_atom_feed(self):
        with patch("feedparser.parse") as mock_parse:
            entry1 = MagicMock()
            entry1.title = "Great Article"
            entry1.link = "https://testblog.example.com/great-article"
            entry1.summary = "A summary."
            del entry1.content  # no content attr

            entry2 = MagicMock()
            entry2.title = "Another Post"
            entry2.link = "https://testblog.example.com/another-post"
            entry2.content = [MagicMock(value="<p>Full content here.</p>")]
            del entry2.summary

            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [entry1, entry2]
            mock_feed.feed.title = "Test Blog"
            mock_parse.return_value = mock_feed

            result = fetch_rss_feeds("https://testblog.example.com/feed", limit=5)
            data = json.loads(result)

            assert data["feed_title"] == "Test Blog"
            assert len(data["articles"]) == 2
            assert data["articles"][0]["title"] == "Great Article"
            assert data["articles"][1]["content"] == "<p>Full content here.</p>"

    def test_limit_respected(self):
        with patch("feedparser.parse") as mock_parse:
            entries = []
            for i in range(10):
                e = MagicMock()
                e.title = f"Article {i}"
                e.link = f"https://example.com/{i}"
                e.summary = f"Summary {i}"
                del e.content
                entries.append(e)

            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = entries
            mock_feed.feed.title = "Feed"
            mock_parse.return_value = mock_feed

            result = fetch_rss_feeds("https://example.com/feed", limit=3)
            data = json.loads(result)
            assert len(data["articles"]) == 3

    def test_bozo_feed_returns_error(self):
        with patch("feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = True
            mock_feed.bozo_exception = Exception("XML parse error")
            mock_parse.return_value = mock_feed

            result = fetch_rss_feeds("https://broken.example.com/feed")
            data = json.loads(result)
            assert "error" in data

    def test_network_exception_returns_error_json(self):
        with patch("feedparser.parse", side_effect=ConnectionError("timeout")):
            result = fetch_rss_feeds("https://unreachable.example.com/feed")
            data = json.loads(result)
            assert "error" in data

    def test_result_is_valid_json(self):
        with patch("feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = []
            mock_feed.feed.title = "Empty Feed"
            mock_parse.return_value = mock_feed

            result = fetch_rss_feeds("https://example.com/feed")
            # Should not raise
            data = json.loads(result)
            assert "articles" in data

    def test_unicode_content_handled(self):
        with patch("feedparser.parse") as mock_parse:
            entry = MagicMock()
            entry.title = "Ääkköset toimivat: ö, ä, å, 中文"
            entry.link = "https://example.com/unicode"
            entry.summary = "Tämä on suomenkielinen artikkeli."
            del entry.content

            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [entry]
            mock_feed.feed.title = "Suomi Feed"
            mock_parse.return_value = mock_feed

            result = fetch_rss_feeds("https://example.com/feed")
            data = json.loads(result)
            assert "Ääkköset" in data["articles"][0]["title"]
