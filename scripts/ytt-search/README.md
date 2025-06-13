# YouTube Transcript Search Tool (`ytt-search`)

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A CLI utility to search YouTube video transcripts for one or more keywords or phrases.  
Supports scanning an entire channel, a single video URL, or a batch of URLs from a file.  
Highlights matches in context, prints timestamps, and generates “jump-to” links.

## Features

- Full **channel scan** via YouTube Data API  
- Single-video search using a direct URL  
- Batch mode: read multiple URLs from a plaintext file  
- Search for one or more comma-separated keywords or multi-word phrases  
- Prints the **video title** (in blue) before each result block  
- Shows **timestamped** jump-links (in yellow)  
- Highlights each keyword with a **lime** / cyan / red / green background and black text  
- Includes one segment of context before & after each match (adjustable)  
- Graceful error handling for missing or disabled transcripts  
- Environment variable support for your YouTube API key

## Installation

1. Clone this repo and `cd` into the script directory:
    ```bash
    git clone https://github.com/4ngel2769/side-projects.git
    cd side-projects/scripts/ytt-search
    ```
2. Install the Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file alongside `yttrsch.py`:
    ```
    OUTUBEY_API_KEY=YOUR_API_KEY_HERE
    ```

## Usage

```bash
python yttrsch.py -k <KEYWORDS> [ -c <CHANNEL_ID> | -v <VIDEO_URL> | -f <FILE> ]
```

- `-k, --keyword`  
  Comma-separate multiple keywords (e.g. `apple,banana,fruit salad`)  
  or wrap a phrase in quotes (e.g. `"machine learning"`).  
- `-c, --channel`  
  Scan all videos in a channel by its ID.  
- `-v, --video`  
  Single YouTube URL.  
- `-f, --file`  
  Path to a text file with one video URL per line.

### Examples

1. Search a channel:
    ```bash
    python yttrsch.py \
      -k "data science,python" \
      -c UC2DjFE7Xf11URZqWBigcVOQ
    ```
2. Search a single video:
    ```bash
    python yttrsch.py \
      -k "deep learning" \
      -v https://www.youtube.com/watch?v=dQw4w9WgXcQ
    ```
3. Batch mode:
    ```bash
    python yttrsch.py \
      -k banana,fruit \
      -f videos.txt
    ```
   `videos.txt`:
    ```
    https://youtu.be/VIDEOID1
    https://youtu.be/VIDEOID2
    ```

## Output

For each video that contains matches, you’ll see:

  • **Video Title** (blue)  
  • One or more lines:
    - A jump-link to the exact timestamp:  
      `https://youtube.com/watch?v=ID&t=123s`
    - Timestamp `(02:03)` in yellow  
    - A snippet of transcript with your keywords highlighted  
      (background in lime/cyan/red/green, text in black)

Example:

  UC Example Video Title

  https://www.youtube.com/watch?v=XYZ123&t=15s  (00:15)  
    …Welcome to our [banana] tutorial on fruit…  

  https://www.youtube.com/watch?v=XYZ123&t=75s  (01:15)  
    …let’s slice a [banana] with Python…

## Troubleshooting

- **“Error: set YOUTUBE_API_KEY in .env”**  
  Ensure `.env` exists, is in the same folder, and contains a valid key.  
- **Quota exceeded**  
  YouTube Data API quotas reset daily. Use a different key or wait.  
- **Missing transcripts**  
  Not all videos have transcripts or may have them disabled.  
- **Slow performance**  
  Batch or channel scans can be lengthy—transcript fetches are rate-limited.

## Contributing

1. Fork this repo.  
2. Create a branch: `git checkout -b feature/improve-search`  
3. Commit: `git commit -am 'Add new search feature'`  
4. Push: `git push origin feature/improve-search`  
5. Open a Pull Request.

## License

MIT © 2025 angeldev0. See [LICENSE](../../LICENSE) for details.

---

**Disclaimer**: Use responsibly. Respect YouTube’s Terms of Service and rate limits.  