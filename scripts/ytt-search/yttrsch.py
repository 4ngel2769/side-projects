# script.py
import argparse
import os
import re
import sys
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build

# ANSI color codes
BLUE      = '\033[94m'
YELLOW    = '\033[93m'
BG_LIME   = '\033[102m'
BG_CYAN   = '\033[46m'
BG_RED    = '\033[41m'
BG_GREEN  = '\033[42m'
BG_PURPLE = '\033[45m'
RED       = '\033[31m'
MAGENTA   = '\033[35m'
CYAN      = '\033[36m'
GREEN     = '\033[32m'
BLACK     = '\033[30m'
WHITE     = '\033[37m'
RESET     = '\033[0m'

# cycle through these for each keyword
KEY_COLORS = [BG_CYAN, BG_LIME, BG_RED, BG_GREEN]

load_dotenv()

def clear_line():
    """Erase the current line."""
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def update_progress(current, total, width=40, prefix="Processing"):
    """Prints an in-place progress bar that stays at the bottom."""
    pct = current / total
    filled = int(pct * width)
    bar = f"[{'=' * filled}{' ' * (width - filled)}]"
    # purple background + black text for prefix + bar
    sys.stdout.write(f"\r{BG_PURPLE}{BLACK}{prefix} {bar} "
                     f"{current}/{total} ({pct:.0%}){RESET}")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write(f"  {BG_GREEN}{BLACK} Done!{RESET}\n")
        sys.stdout.flush()

def extract_video_id(url):
    m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:\&|$)', url)
    return m.group(1) if m else None

def parse_channel_input(youtube, raw):
    """
    Accepts a raw channel ID, or URL/handle, and returns a valid channel ID.
    """
    if raw.startswith("http"):
        p = urlparse(raw)
        parts = p.path.strip("/").split("/")
        # e.g. /@handle
        if parts[0].startswith("@"):
            return resolve_handle(youtube, parts[0][1:])
        # e.g. /channel/UC...
        if parts[0] == "channel" and len(parts) > 1:
            return parts[1]
        # fallback: custom path
        return resolve_handle(youtube, parts[-1])
    # assume it's already an ID
    return raw

def resolve_handle(youtube, name):
    """
    Try channels().list(forUsername=…) then search().list(type=channel, q=…)
    """
    # legacy username
    res = youtube.channels().list(part="id", forUsername=name).execute()
    items = res.get("items", [])
    if items:
        return items[0]["id"]
    # fallback search
    res = youtube.search().list(
        part="id", type="channel", q=name, maxResults=1
    ).execute()
    items = res.get("items", [])
    if items:
        return items[0]["id"]["channelId"]
    raise ValueError(f"Cannot resolve channel identifier: {name}")

def get_video_ids_from_channel(youtube, channel_id):
    ids, req = [], youtube.search().list(
        part="id", channelId=channel_id, maxResults=50, type="video"
    )
    while True:
        res = req.execute()
        ids += [item['id']['videoId'] for item in res.get('items',[])]
        token = res.get('nextPageToken')
        if not token: break
        req = youtube.search().list(
            part="id", channelId=channel_id,
            maxResults=50, pageToken=token, type="video"
        )
    return ids

def fetch_transcription_segments(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id), None
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None, f"[{video_id}] no transcript: {e}"
    except Exception as e:
        return None, f"[{video_id}] error: {e}"

def format_timestamp(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def highlight(text, keywords):
    """
    Highlight each keyword with a lime background and its own color.
    """
    for idx, kw in enumerate(keywords):
        color = KEY_COLORS[idx % len(KEY_COLORS)]
        pattern = re.compile(f"(?i)({re.escape(kw)})")
        text = pattern.sub(f"{color}{BLACK}\\1{RESET}", text)
    return text

def get_video_title(youtube, video_id):
    try:
        resp = youtube.videos().list(part="snippet", id=video_id).execute()
        items = resp.get("items", [])
        if items:
            return items[0]["snippet"]["title"]
    except:
        pass
    return "Unknown Title"

def main():
    p = argparse.ArgumentParser(description='Search YouTube transcripts by keyword(s).')
    p.add_argument('-k','--keyword', required=True, help='Comma-separated keywords or a phrase')
    p.add_argument('-c','--channel', help='Channel ID or URL')
    p.add_argument('-v','--video', help='Single YouTube URL')
    p.add_argument('-f','--file', help='Path to file of YouTube URLs')
    args = p.parse_args()

    # parse keywords
    keywords = [k.strip() for k in args.keyword.split(',') if k.strip()]

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: set YOUTUBE_API_KEY in .env")
        return

    yt = build('youtube','v3', developerKey=api_key)
    vids = []

    if args.channel:
        try:
            cid = parse_channel_input(yt, args.channel)
            vids += get_video_ids_from_channel(yt, cid)
        except Exception as e:
            print(f"Channel fetch error: {e}")

    if args.video:
        vid = extract_video_id(args.video)
        if vid: vids.append(vid)
        else: print(f"Bad video URL: {args.video}")

    if args.file:
        if os.path.isfile(args.file):
            with open(args.file, encoding='utf-8') as f:
                for line in f:
                    link = line.strip()
                    vid = extract_video_id(link)
                    if vid: vids.append(vid)
                    else: print(f"Bad URL in {args.file}: {link}")
        else:
            print(f"File not found: {args.file}")

    vids = list(dict.fromkeys(vids))
    total = len(vids)
    if total == 0:
        print("No videos to process.")
        return

    errors = []

    for idx, vid in enumerate(vids, start=1):
        segments, err = fetch_transcription_segments(vid)
        if err:
            errors.append(err)
        else:
            # find matches...
            matches = []
            CONTEXT = 1
            for i, seg in enumerate(segments):
                text = seg.get('text','')
                if any(kw.lower() in text.lower() for kw in keywords):
                    start_idx = max(0, i - CONTEXT)
                    end_idx   = min(len(segments), i + CONTEXT + 1)
                    ctx = " ".join(s.get('text','') for s in segments[start_idx:end_idx])
                    ts = seg.get('start', 0)
                    link = f"https://www.youtube.com/watch?v={vid}&t={int(ts)}s"
                    tstr = format_timestamp(ts)
                    snippet = highlight(ctx, keywords)
                    matches.append((link, tstr, snippet))

            if matches:
                clear_line()
                title = get_video_title(yt, vid)
                print(f"\n{BLUE}{title}{RESET}\n")
                for link, tstr, snippet in matches:
                    print(f"{link}  ({YELLOW}{tstr}{RESET})\n  …{snippet}…\n")

        # always redraw bar after handling one video
        update_progress(idx, total)

    if errors:
        print("\nErrors:")
        for e in errors:
            print(" ", e)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopping..")
        sys.exit(0)
