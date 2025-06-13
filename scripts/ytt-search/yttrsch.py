# script.py
import argparse
import os
import re
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
RED       = '\033[31m'
MAGENTA   = '\033[35m'
CYAN      = '\033[36m'
GREEN     = '\033[32m'
BLACK     = '\033[30m'
RESET     = '\033[0m'

# cycle through these for each keyword
KEY_COLORS = [BG_CYAN, BG_LIME, BG_RED, BG_GREEN]

load_dotenv()

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:\&|$)'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_video_ids_from_channel(youtube, channel_id):
    ids = []
    req = youtube.search().list(part='id', channelId=channel_id,
                                maxResults=50, type='video')
    while True:
        res = req.execute()
        ids += [item['id']['videoId'] for item in res.get('items',[])]
        token = res.get('nextPageToken')
        if not token: break
        req = youtube.search().list(part='id', channelId=channel_id,
                                    maxResults=50, pageToken=token, type='video')
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
    except Exception:
        pass
    return "Unknown Title"

def main():
    p = argparse.ArgumentParser(description='Search YouTube transcripts by keyword(s).')
    p.add_argument('-k','--keyword', required=True,
                   help='Comma-separated keywords or a phrase (e.g. "word1,word2,phrase here")')
    p.add_argument('-c','--channel', help='YouTube channel ID.')
    p.add_argument('-v','--video', help='Single YouTube URL to scan.')
    p.add_argument('-f','--file', help='Path to file with one YouTube URL per line.')
    args = p.parse_args()

    # split into list; if no comma, it's one element (phrase)
    raw = args.keyword
    keywords = [k.strip() for k in raw.split(',') if k.strip()]

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: set YOUTUBE_API_KEY in .env")
        return

    yt = build('youtube','v3', developerKey=api_key)
    vids = []

    if args.channel:
        try:
            vids += get_video_ids_from_channel(yt, args.channel)
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
                    if not link: continue
                    vid = extract_video_id(link)
                    if vid: vids.append(vid)
                    else: print(f"Bad URL in {args.file}: {link}")
        else:
            print(f"File not found: {args.file}")

    vids = list(dict.fromkeys(vids))
    if not vids:
        print("No videos to process.")
        return

    errors = []

    for vid in vids:
        segments, err = fetch_transcription_segments(vid)
        if err:
            errors.append(err)
            continue

        matches = []
        # include one segment before and after for context
        CONTEXT = 1
        for i, seg in enumerate(segments):
            text = seg.get('text','')
            low = text.lower()
            if any(kw.lower() in low for kw in keywords):
                # determine slice of segments for context
                start_idx = max(0, i - CONTEXT)
                end_idx   = min(len(segments), i + CONTEXT + 1)
                context_text = " ".join(s.get('text','') for s in segments[start_idx:end_idx])

                ts = seg.get('start', 0)
                tstr = format_timestamp(ts)
                link = f"https://www.youtube.com/watch?v={vid}&t={int(ts)}s"
                snippet = highlight(context_text, keywords)
                matches.append((link, tstr, snippet))

        if matches:
            title = get_video_title(yt, vid)
            print(f"\n{BLUE}{title}{RESET}\n")
            for link, tstr, snippet in matches:
                print(f"{link}  ({YELLOW}{tstr}{RESET})\n  …{snippet}…\n")

    if errors:
        print("Errors:")
        for e in errors:
            print(" ", e)

if __name__ == "__main__":
    main()
