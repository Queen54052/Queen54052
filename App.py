# app.py
import os
import random
import requests
import mimetypes
import tempfile
from trending import get_trending_hashtags
import tweepy

def create_api_v1():
    # OAuth1 (tweepy API v1.1) - diperlukan untuk media_upload + update_status
    consumer_key = os.getenv("API_KEY")
    consumer_secret = os.getenv("API_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_secret = os.getenv("ACCESS_SECRET")

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_secret
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def download_image_from_url(url):
    if not url:
        return None
    try:
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        ext = None
        if "image" in content_type:
            ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if not ext:
            # fallback from URL path
            parsed = url.split("?")[0]
            if "." in parsed:
                ext = "." + parsed.split(".")[-1]
            else:
                ext = ".jpg"
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return tmp_path
    except Exception as e:
        print("Failed to download image:", e)
        return None

def build_caption(title, desc, hashtags):
    parts = []
    if title:
        parts.append(title)
    if desc:
        parts.append(desc)
    if hashtags:
        # hashtags is a list -> join by space
        parts.append(" ".join(hashtags))
    return "\n\n".join(parts)

def main():
    api = create_api_v1()

    # Ambil values dari ENV (set di GitHub Secrets)
    image_url = os.getenv("IMAGE_URL", "").strip()  # contoh: https://example.com/pic.jpg
    title = os.getenv("TWEET_TITLE", "Update Trending Hari Ini 🔥")
    desc = os.getenv("TWEET_DESC", "Info singkat: lihat hashtag trending berikut.")
    # ambil trending (bisa kosong)
    hashtags = get_trending_hashtags() or []

    caption = build_caption(title, desc, hashtags[:5])

    # Download image dari URL (jadi file lokal), jika URL disediakan
    media_path = None
    if image_url:
        print("Downloading image from URL:", image_url)
        media_path = download_image_from_url(image_url)
        if not media_path:
            print("Download gagal — akan kirim tweet tanpa gambar.")

    try:
        if media_path:
            print("Uploading media:", media_path)
            media = api.media_upload(media_path)
            print("Posting tweet with media...")
            api.update_status(status=caption, media_ids=[media.media_id_string])
            print("Tweet terkirim dengan gambar.")
        else:
            print("Posting tweet tanpa media...")
            api.update_status(status=caption)
            print("Tweet terkirim tanpa gambar.")
    except tweepy.TweepError as e:
        print("Tweepy error:", e)
    except Exception as e:
        print("Error saat posting:", e)
    finally:
        # cleanup temporary file
        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
            except:
                pass

if __name__ == "__main__":
    main()
