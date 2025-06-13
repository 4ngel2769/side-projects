# YouTube Transcript Search Tool (`ytt-search`)

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A CLI utility to search YouTube video transcripts for one or more keywords or phrases.  
Supports scanning an entire channel (by ID, URL or handle), a single video URL, or a batch of URLs from a file.  
Highlights matches in context, prints timestamps, and generates "jump-to" links, shows a progress bar, and summarizes keywords that weren't found.

---

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

---

## Usage

```bash
python yttrsch.py \
  -k <KEYWORDS> \
  [-c <CHANNEL_ID|URL|@handle>] \
  [-v <VIDEO_URL>] \
  [-f <FILE>] \
  [-s newest|oldest|popular] \
  [-m <MAX_VIDEOS>] \
  [-V]
```

Arguments:

- `-k, --keyword`  
  Comma-separated keywords or a quoted phrase (e.g. `apple,banana` or `"machine learning"`).  
- `-c, --channel`  
  Channel ID (`UC…`), URL (`https://youtube.com/channel/...`), or handle (`@name`).  
- `-v, --video`  
  Single YouTube URL.  
- `-f, --file`  
  Path to a text file containing one video URL per line.  
- `-s, --sort`  
  Order channel videos by `newest` (default), `oldest`, or `popular` (view count).  
- `-m, --maximum`  
  Maximum number of videos to process (supports `k`/`m` suffixes, e.g. `1.3k`, `2m`).  
- `-V, --version`  
  Show tool version and exit.

---

## Examples

1. **Show version**  
   ```bash
   python yttrsch.py -V
   ```

2. **Channel scan, newest first, limit 100**  
   ```bash
   python yttrsch.py \
     -k banana,fruit \
     -c https://www.youtube.com/@upir_upir \
     -s newest \
     -m 100
   ```

3. **Channel scan, oldest first**  
   ```bash
   python yttrsch.py \
     -k "data science, machine learning" \
     -c UC2DjFE7Xf11URZqWBigcVOQ \
     -s oldest
   ```

4. **Single video**  
   ```bash
   python yttrsch.py \
     -k "deep learning" \
     -v https://youtu.be/dQw4w9WgXcQ
   ```

5. **Batch mode from `example_links.txt`**  
   ```bash
   python yttrsch.py -k hello -f example_links.txt
   ```

---

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

When complete, it turns green and lists any keywords not found:
```
Processing [====================] 20/20 (100%)  Done!

Keywords not found:
  - apple
  - orange
```

## Troubleshooting

- **Error: set YOUTUBE_API_KEY in .env**
> Ensure the file exists, is in the script folder, and contains a valid key.
- **Quota exceeded**
> YouTube Data API quotas reset daily. Use another key or wait.
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