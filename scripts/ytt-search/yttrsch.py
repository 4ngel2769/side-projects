################################################
# YTTS - YouTube Transcript Search Tool
# Copyright (c) 2025 angeldev0
# Code written by angeldev0
# License: MIT
################################################

import argparse
import os
import re
import sys
import time
import isodate
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
    Accepts:
      • raw channel ID (UC…)
      • bare handle (@name)
      • full channel URL or @handle URL
    and returns the proper UC… ID.
    """
    # bare handle
    if raw.startswith("@"):
        return resolve_handle(youtube, raw[1:])
    # full URL
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

def parse_max_videos(val):
    """Parse human-friendly video count (e.g. 1.3k, 2m) into integer."""
    v = val.lower().replace(',', '').strip()
    if v.endswith('k'):
        return int(float(v[:-1]) * 1_000)
    if v.endswith('m'):
        return int(float(v[:-1]) * 1_000_000)
    return int(v)

def get_video_ids_from_channel(youtube, channel_id, sort_order='newest', max_videos=None):
    """
    Fetch video IDs from a channel with optional sort and limit.
    sort_order: 'newest', 'oldest', or 'popular'
    max_videos: int or None
    """
    ids = []
    # API order param
    order_param = 'viewCount' if sort_order == 'popular' else 'date'
    req = youtube.search().list(
        part="id", channelId=channel_id,
        maxResults=50, type="video",
        order=order_param
    )
    while True:
        res = req.execute()
        batch = [item['id']['videoId'] for item in res.get('items', [])]
        ids.extend(batch)
        if max_videos and len(ids) >= max_videos:
            ids = ids[:max_videos]
            break
        token = res.get('nextPageToken')
        if not token:
            break
        req = youtube.search().list(
            part="id", channelId=channel_id,
            maxResults=50, pageToken=token,
            type="video", order=order_param
        )
    if sort_order == 'oldest':
        ids.reverse()
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

class VersionAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, version="1.0.0", help="Show version and exit"):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        msg = f"""
YTTS - YouTube Transcript Search Tool
Version: {self.version}
Author: angeldev0
License: MIT
"""
        print(msg)
        parser.exit()

def parse_length_expr(expr: str):
    """Parse '+5m' or '-2h' (or '30') into (op, seconds)."""
    m = re.match(r'([+-])(\d+(\.\d+)?)([smh])?$', expr.strip())
    if not m:
        raise argparse.ArgumentTypeError(f"Bad length filter: {expr!r}")
    sign, num, _, unit = m.groups()
    op = '>' if sign == '+' else '<'
    num = float(num)
    seconds = num * {'s':1, 'm':60, 'h':3600}[unit or 's']
    return op, seconds

def fetch_video_durations(youtube, vids:list[str]) -> dict[str,int]:
    """Batch-fetch each video’s duration in seconds via contentDetails."""
    durations = {}
    for i in range(0, len(vids), 50):
        batch = vids[i:i+50]
        resp = youtube.videos().list(
            part="contentDetails",
            id=",".join(batch)
        ).execute()
        for item in resp.get("items", []):
            vid = item["id"]
            iso = item["contentDetails"]["duration"]
            durations[vid] = int(isodate.parse_duration(iso).total_seconds())
    return durations

def main():
    p = argparse.ArgumentParser(description='Search YouTube transcripts by keyword(s).')
    # version flag
    p.add_argument('-V','--version', action=VersionAction, help='Show version and exit')
    p.add_argument('-k','--keyword', required=True, help='Comma-separated keywords or a phrase')
    p.add_argument('-c','--channel', help='Channel ID, URL or handle')
    p.add_argument('-s','--sort',
                   choices=['newest','oldest','popular'],
                   default='newest',
                   help='Sort channel videos by newest, oldest, or popular (view count)')
    p.add_argument('-m','--maximum',
                   type=parse_max_videos,
                   help='Maximum number of channel videos to process (e.g. 1.3k, 2m)')
    # remap single-video to -v → uppercase V is taken by version
    p.add_argument('-v','--video', help='Single YouTube URL')
    p.add_argument('-f','--file', help='Path to file of YouTube URLs')
    p.add_argument('-x','--length', nargs='+', metavar='EXPR',
                   help="Filter by video duration with + or - prefixes, e.g. -5m +2h 30 (seconds)")
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
            vids += get_video_ids_from_channel(
                yt, cid,
                sort_order=args.sort,
                max_videos=args.maximum
            )
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
    if not vids:
        print("No videos to process."); return

    # apply length filters (allow space/comma‐separated in one string or multiple args)
    if args.length:
        # split every token on commas or whitespace
        raw_tokens = []
        for chunk in args.length:
            raw_tokens += re.split(r'[,\s]+', chunk.strip())
        # filter out empty strings
        raw_tokens = [t for t in raw_tokens if t]
        try:
            exprs = [parse_length_expr(tok) for tok in raw_tokens]
        except argparse.ArgumentTypeError as e:
            print(e)
            return

        durations = fetch_video_durations(yt, vids)
        filtered = []
        for vid in vids:
            d = durations.get(vid)
            if d is None:
                continue  # skip if we can't get duration
            ok = True
            for op, secs in exprs:
                if op == '<'  and not (d <  secs): ok = False
                if op == '<=' and not (d <= secs): ok = False
                if op == '>'  and not (d >  secs): ok = False
                if op == '>=' and not (d >= secs): ok = False
            if ok:
                filtered.append(vid)
        vids = filtered

    total = len(vids)
    if total == 0:
        print("No videos match length filters."); return

    errors = []
    # track which keywords were actually found
    found_keywords = set()

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
                low_text = text.lower()
                # record any keyword found in this segment
                for kw in keywords:
                    if kw.lower() in low_text:
                        found_keywords.add(kw.lower())
                if any(kw.lower() in low_text for kw in keywords):
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

    # after processing all videos report any keywords not found
    missing = [kw for kw in keywords if kw.lower() not in found_keywords]
    if missing:
        print("\nKeywords not found:")
        for kw in missing:
            print(f"  - {kw}")

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
