# trending.py
import requests
from bs4 import BeautifulSoup

def get_trending_hashtags():
    try:
        url = "https://trends24.in/indonesia/"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        tags = []
        for a in soup.select(".trend-card ol li a"):
            text = a.get_text(strip=True)
            if text.startswith("#"):
                tags.append(text)
        # kembalikan max 5 hashtag
        return tags[:5]
    except Exception as e:
        print("Cannot fetch trending:", e)
        return []
