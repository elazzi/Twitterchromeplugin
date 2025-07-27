# Twitter Bookmark Archiver (Python)

This is a Python script that lets you export your Twitter Bookmarks, including all media (photos and videos, as well as fully expanded URLs) attached to those tweets.

## How to run this script

1.  **Install Python 3.**
2.  **Download this script.**
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a Twitter Developer account and a new app.**
    You will need to apply for "Elevated" access, but the approval process is usually immediate.
    When creating your app, set the "App permissions" to "Read", the "Type of App" to "Native App", and the "Callback URI" to `http://localhost:3000`.
5.  **Create a file named `.env` in the same directory as the script, with the following contents:**
    ```
    TWITTER_CLIENT_ID=<your_client_id>
    TWITTER_CLIENT_SECRET=<your_client_secret>
    ```
6.  **Run the script:**
    ```bash
    python3 twitter_archiver.py
    ```
7.  You will see a login URL. Click it, and authorize the app.
8.  The script will start downloading your bookmarks and media.
9.  Once it is complete, you will find an `index.html` file and a `media` folder in the same directory.

## Usage

```
usage: twitter_archiver.py [-h] [--no-html]

optional arguments:
  -h, --help  show this help message and exit
  --no-html   Disable HTML output
```