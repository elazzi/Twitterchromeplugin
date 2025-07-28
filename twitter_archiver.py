import os
import json
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import time
import tweepy
import aiohttp
import asyncio
from urllib.parse import urlparse
import tweepy

# Your client credentials
client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")

# Scopes
scopes = ["bookmark.read", "users.read", "tweet.read"]

def login():
    """
    Handles the OAuth2 authentication with Twitter.
    """
    if os.path.exists(".auth"):
        with open(".auth", "r") as f:
            auth_data = json.load(f)
            # Check if the token is expired
            if auth_data.get("expiry") > time.time() + 5 * 60:
                return tweepy.Client(auth_data["access_token"])

    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=client_id,
        redirect_uri="http://localhost:3000",
        scope=scopes,
        client_secret=client_secret,
    )

    print(f"Please go here and authorize: {oauth2_user_handler.get_authorization_url()}")

    # Get the authorization verifier code from the callback url
    redirect_response = input("Paste the full redirect URL here: ")

    # Fetch the access token
    response = oauth2_user_handler.fetch_token(redirect_response)
    access_token = response["access_token"]

    # Save the token
    with open(".auth", "w") as f:
        response["expiry"] = time.time() + response["expires_in"]
        json.dump(response, f)

    return tweepy.Client(access_token)

def get_bookmarks(client):
    """
    Fetches the user's bookmarks.
    """
    bookmarks = client.get_bookmarks(expansions=["author_id", "attachments.media_keys"], media_fields=["url", "preview_image_url", "variants"])
    return bookmarks

def get_timeline(client):
    """
    Fetches the user's "following" timeline.
    """
    user = client.get_me()
    timeline = client.get_users_tweets(user.data.id, max_results=100, expansions=["author_id", "attachments.media_keys"], media_fields=["url", "preview_image_url", "variants"])
    return timeline

def to_dict(obj):
    """
    Converts a tweepy object to a dictionary.
    """
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    elif hasattr(obj, "data"):
        return to_dict(obj.data)
    elif hasattr(obj, "__dict__"):
        return {key: to_dict(value) for key, value in obj.__dict__.items() if not key.startswith("_")}
    else:
        return obj

async def download_media(all_bookmarks):
    """
    Downloads the media associated with the bookmarks.
    """
    download_list = set()
    for bm in all_bookmarks:
        for media in bm.get("media", []):
            if media.get("type") == "photo":
                download_list.add(media.get("url"))
            elif media.get("type") in ["video", "animated_gif"]:
                variants = media.get("variants", [])
                variants.sort(key=lambda x: x.get("bit_rate", 0), reverse=True)
                if variants:
                    download_list.add(variants[0].get("url"))
                download_list.add(media.get("preview_image_url"))
            # Check if author is a list and access the first element if it exists
            author = bm.get("author", [])
            if isinstance(author, list) and author:
                author = author[0]  # Take the first author if the list is not empty
            else:
                author = {}  # Assign an empty dictionary if author is not a list or is empty

        if author:
            download_list.add(author.get("profile_image_url"))

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in download_list:
            if url:
                tasks.append(download_file(session, url))
        await asyncio.gather(*tasks)

async def download_file(session, url):
    """
    Downloads a single file.
    """
    u = urlparse(url)
    filename = os.path.join("media", os.path.basename(u.path))
    if os.path.exists(filename):
        return
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print(f"Downloading {url}")
    async with session.get(url) as response:
        with open(filename, "wb") as f:
            f.write(await response.read())
    print(f"Done {url}")

def generate_html(all_bookmarks):
    """
    Generates an HTML file with the tweets and media, one tweet per page.
    """
    for i, bm in enumerate(all_bookmarks):
        filename = f"tweet_{i + 1}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("<html><head><title>Twitter Bookmark</title></head><body>")

            tweet = bm.get("tweet", {})
            media = bm.get("media", [])
            # Check if author is a list and access the first element if it exists
            author = bm.get("author", [])
            if isinstance(author, list) and author:
                author = author[0]  # Take the first author if the list is not empty
            else:
                author = {}  # Assign an empty dictionary if author is not a list or is empty

            f.write(f"<div>")
            f.write(f"<p><b>{author.get('name', 'N/A')}</b> (@{author.get('username', 'N/A')})</p>") # added default values to avoid errors
            f.write(f"<p>{tweet.get('text')}</p>")
            for m in media:
                if m.get("type") == "photo":
                    f.write(f"<img src='media/{os.path.basename(m.get('url'))}'>")
                elif m.get("type") in ["video", "animated_gif"]:
                    variants = m.get("variants", [])
                    variants.sort(key=lambda x: x.get("bit_rate", 0), reverse=True)
                    if variants:
                        f.write(f"<video controls><source src='media/{os.path.basename(variants[0].get('url'))}' type='video/mp4'></video>")
            f.write("</div><hr>")
            f.write("</body></html>")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-html", action="store_true", help="Disable HTML output")
    parser.add_argument("--timeline", action="store_true", help="Fetch timeline instead of bookmarks")
    args = parser.parse_args()

    if args.timeline:
        filename = "timeline.json"
    else:
        filename = "all_bookmarks.json"

    all_data = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            all_data = json.load(f)
    else:
        client = login()
        if args.timeline:
            data = get_timeline(client)
            filename = "timeline.json"
        else:
            data = get_bookmarks(client)
            filename = "all_bookmarks.json"
    if not all_data:
        if data and data.data:
            for tweet in data.data:
                media = data.includes.get("media", [])
                author = data.includes.get("users", [])
                bm = {
                    "tweet": to_dict(tweet),
                    "media": to_dict(media),
                    "author": to_dict(author),
                }
                all_data.append(bm)
            with open(filename, "w") as f:
                json.dump(all_data, f, indent=2)

    asyncio.run(download_media(all_data))
    if not args.no_html:
        generate_html(all_data)
