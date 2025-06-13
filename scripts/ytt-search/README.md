# YouTube Transcript Search Tool (`ytt-search`)

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A CLI utility to search YouTube video transcripts for one or more keywords or phrases.
Supports scanning an entire channel (by ID, URL or handle), a single video URL, or a batch of URLs from a file.
Highlights matches in context, prints timestamps, and generates “jump-to” links with an in-place progress bar.

## Features

- Full **channel scan** via YouTube Data API
- Accepts channel **URL**, **handle** (`@name`) or **ID** (`UC…`)
- **Single-video** search by URL
- **Batch** mode: read multiple URLs from a plaintext file
- Search for **multiple** comma-separated keywords or **multi-word phrases**
- Shows **timestamped** jump-links (yellow)
- Highlights each keyword with a **colored background** (lime/cyan/red/green) and black text
- Includes **one segment of context** before & after each match (adjustable)
- **Progress bar** at the bottom, updates per video, turns green “Done!” when complete
- Graceful **CTRL+C** handling (`stopping..`)
- Error handling for missing or disabled transcripts
- **.env** support for your YouTube API key

## Installation

1. Clone this repo and `cd` into the script folder:
    ```bash
    git clone https://github.com/4ngel2769/side-projects.git
    cd side-projects/scripts/ytt-search
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file alongside `yttrsch.py`:
    ```dotenv
    YOUTUBE_API_KEY=YOUR_API_KEY_HERE
    ```

## Usage

```bash
python yttrsch.py \
  -k <KEYWORDS> \
  [-c <CHANNEL_ID|URL|@handle>] \
  [-v <VIDEO_URL>] \
  [-f <FILE>]
```

- `-k, --keyword`
  Comma-separate multiple keywords (e.g. `apple,banana`)
  or wrap a multi-word phrase in quotes (e.g. `"machine learning"`).
- `-c, --channel`
  Channel ID (`UC…`), URL (`https://www.youtube.com/channel/…`), or handle (`@name`).
- `-v, --video`
  Single YouTube URL.
- `-f, --file`
  Path to a text file with one YouTube URL per line.

## Examples

1. **Channel scan**:
    ```bash
    python yttrsch.py \
      -k "data science,python" \
      -c https://www.youtube.com/@upir_upir
    ```
2. **Single video**:
    ```bash
    python yttrsch.py \
      -k "deep learning" \
      -v https://www.youtube.com/watch?v=dQw4w9WgXcQ
    ```
3. **Batch mode**:
    ```bash
    python yttrsch.py \
      -k banana,fruit \
      -f videos.txt
    ```
   `videos.txt`:
    ```
    https://youtu.be/VIDEOID1
    https://youtu.be/VIDEOID2
    https://www.youtube.com/watch?v=VIDEOID3
    ```

## Output

For each video containing matches you'll see:

1. **Title** (blue)
2. One or more lines per match:
   - Jump-link:
     `https://www.youtube.com/watch?v=<ID>&t=<seconds>s`
   - **Timestamp** in yellow `(MM:SS)`
   - **Context snippet** (one line before/after), keywords highlighted

Example:
```
My Example Video Title

https://www.youtube.com/watch?v=XYZ123&t=15s  (00:15)
  …Welcome to our [banana] cooking tutorial…

https://www.youtube.com/watch?v=XYZ123&t=75s  (01:15)
  …let's slice the [banana] with a spoon…
```

A progress bar remains at the bottom:
```
Processing [=========           ] 5/20 (25%)  Done!
```

When complete, it turns green:
```
Processing [====================] 20/20 (100%)  Done!
```

## Troubleshooting

- **Error: set YOUTUBE_API_KEY in .env**
> Ensure the file exists, is in the script folder, and contains a valid key.
- **Quota exceeded**
> YouTube Data API quotas reset daily—use another key or wait.
- **Missing transcripts**
> Some videos disable transcripts or have no generated captions.
- **Slow performance**
> Channel or large batch scans can take time—transcript fetches are rate-limited.

## Contributing

1. Fork the repo
2. Create a branch:
   `git checkout -b feature/name`
3. Commit your changes:
   `git commit -m "Add new feature"` 
4. Push:
   `git push origin feature/name`
5. Open a Pull Request

## License

MIT © 2025 angeldev0. See [LICENSE](../../LICENSE) for details.

---

**Disclaimer**: Use responsibly. Respect YouTube's Terms of Service and rate limits.