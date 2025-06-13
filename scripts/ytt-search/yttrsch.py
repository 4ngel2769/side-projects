# script.py
import argparse
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    Supports formats like:
      - https://youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/watch?v=VIDEO_ID
    """
    # Regular expression to extract the video ID from the URL
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_ids_from_channel(youtube, channel_id):
    """Retrieve all video IDs from a given channel."""
    video_ids = []
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=50,
        type="video"
    )
    response = request.execute()
    video_ids.extend([item['id']['videoId'] for item in response.get('items', [])])

    # Paginate through results if needed
    while 'nextPageToken' in response:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video",
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        video_ids.extend([item['id']['videoId'] for item in response.get('items', [])])
    return video_ids

def fetch_transcription(video_id):
    """Fetch transcript for a single video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t.get('text', '') for t in transcript]), None
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None, f"Transcript unavailable for video {video_id}: {e}"
    except Exception as e:
        return None, f"Unexpected error fetching transcript for {video_id}: {e}"

def main():
    parser = argparse.ArgumentParser(description='Search YouTube video/channel transcripts.')
    parser.add_argument('-k', '--keyword', required=True, help='Keyword or phrase to search for.')
    parser.add_argument('-c', '--channel', help='YouTube channel ID.')
    parser.add_argument('-v', '--video', help='Single YouTube link (e.g. https://youtu.be/XYZ).')
    parser.add_argument('-f', '--file', help='Path to file with multiple YouTube video links.')
    args = parser.parse_args()

    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        print("Error: YouTube API key not found. Set it in .env.")
        return

    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    # Collect all video IDs
    video_ids = []

    if args.channel:
        try:
            video_ids.extend(get_video_ids_from_channel(youtube, args.channel))
        except Exception as e:
            print(f"Error fetching videos for channel {args.channel}: {e}")

    if args.video:
        vid = extract_video_id(args.video)
        if vid:
            video_ids.append(vid)
        else:
            print(f"Error: Could not extract video ID from {args.video}")

    if args.file:
        if os.path.isfile(args.file):
            with open(args.file, 'r', encoding='utf-8') as f:
                for line in f:
                    link = line.strip()
                    if link:
                        vid = extract_video_id(link)
                        if vid:
                            video_ids.append(vid)
                        else:
                            print(f"Error: Could not extract ID from '{link}'")
        else:
            print(f"Error: File not found: {args.file}")

    video_ids = list(dict.fromkeys(video_ids))
    if not video_ids:
        print("No valid video IDs found.")
        return

    matched_videos = []
    errors = []
    keyword_lower = args.keyword.lower()

    for vid_id in video_ids:
        text, error = fetch_transcription(vid_id)
        if error:
            errors.append(error)
        elif text and keyword_lower in text.lower():
            matched_videos.append(vid_id)

    # Print matching video IDs
    for video_id in matched_videos:
        print(f"https://www.youtube.com/watch?v={video_id}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(err)

if __name__ == "__main__":
    main()
