import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as finwise_app


class NewsFeedTests(unittest.TestCase):
    @mock.patch.object(finwise_app.requests, "get")
    def test_get_news_uses_live_rss_feed_without_api_key(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
        <rss version=\"2.0\">
          <channel>
            <title>Google News</title>
            <item>
              <title>RBI signals rate cut hopes for Indian markets</title>
              <link>https://example.com/1</link>
              <description>Indian markets rally after central bank comments.</description>
              <pubDate>Wed, 30 Oct 2024 09:00:00 GMT</pubDate>
              <source url=\"https://example.com\">Market Wire</source>
            </item>
            <item>
              <title>Nifty climbs on strong bank earnings</title>
              <link>https://example.com/2</link>
              <description>Banking stocks push the broader index higher.</description>
              <pubDate>Wed, 30 Oct 2024 10:00:00 GMT</pubDate>
              <source url=\"https://example.com\">Business Desk</source>
            </item>
          </channel>
        </rss>"""
        mock_get.return_value = mock_response

        with mock.patch.object(finwise_app, "NEWS_API_KEY", ""):
            articles = finwise_app.get_news("finance", 2)

        self.assertEqual(len(articles), 2)
        self.assertIn("RBI", articles[0]["title"])
        self.assertIn("source", articles[0])
        self.assertNotIn("Add a NewsAPI key", articles[0]["title"])

    @mock.patch.object(finwise_app.requests, "get")
    def test_extract_article_image_reads_og_image_metadata(self, mock_get):
        html = """
        <html><head>
            <meta property="og:image" content="https://example.com/image.jpg">
        </head></html>
        """
        mock_get.return_value = mock.Mock(text=html, raise_for_status=mock.Mock(), url="https://example.com/article")

        image_url = finwise_app.extract_article_image("https://example.com/article")

        self.assertEqual(image_url, "https://example.com/image.jpg")


if __name__ == "__main__":
    unittest.main()
