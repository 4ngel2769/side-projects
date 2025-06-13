# YouTube Transcript Search Tool

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A powerful Python utility that searches for keywords within YouTube video transcripts across an entire channel or specific videos. Perfect for researchers, content analyzers, or anyone looking to find specific mentions in YouTube content.

## Features

- **Full channel scanning** with YouTube API integration
- **Search individual videos** using direct YouTube links
- **Batch video mode** with a specified file of YouTube video links
- **Automatic transcript fetching** for all videos
- **Keyword searching** across transcripts
- **Error handling** for videos with disabled or missing transcripts
- **Direct video links** to matching results
- **Batch processing** of large video collections
- **Smart API utilization** with pagination support
- **Environment variable configuration** for API keys

## Installation

### Prerequisites
- Python 3.7 or higher
- YouTube Data API key
- Git

1. Clone the repository:
```bash
git clone https://github.com/4ngel2769/side-projects.git
cd side-projects/scripts/ytt-search
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the directory with your YouTube API key:
```
YOUTUBE_API_KEY=your_api_key_here
```

## Usage

### Basic Command (Channel)
```bash
python yttrsch.py --keyword [KEYWORD] --channel [CHANNEL_ID]
```

### Single Video
```bash
python yttrsch.py --keyword [KEYWORD] --video https://www.youtube.com/watch?v=SOME_VIDEOID
```

### Multiple Videos via File
```bash
python yttrsch.py --keyword [KEYWORD] --file videos.txt
```
Where `videos.txt` contains one YouTube video link per line.

### Full Options
```bash
python yttrsch.py \
  --keyword "specific phrase" \         # Keyword or phrase to search
  --channel UC1234567890abcdef \        # YouTube channel ID
  --video https://youtu.be/EXAMPLE123   # Optional single video link
  --file videos.txt                     # Optional path to a file of links
```

### Arguments

| Argument        | Short | Required | Description                                                                          |
|-----------------|-------|----------|--------------------------------------------------------------------------------------|
| `--keyword`     | `-k`  | Yes      | Keyword or phrase to search for in transcripts                                      |
| `--channel`     | `-c`  | No       | YouTube channel ID to search                                                        |
| `--video`       | `-v`  | No       | Single YouTube link (e.g., https://youtu.be/XYZ)                                    |
| `--file`        | `-f`  | No       | Path to a file containing multiple YouTube video links to search (one per line)     |
| `--help`        | `-h`  | No       | Show help message                                                                    |

## Examples

1. **Search for AI discussions on a channel**:
```bash
python yttrsch.py \
  --keyword "artificial intelligence" \
  --channel UC2DjFE7Xf11URZqWBigcVOQ
```

2. **Search a single video for mentions of a specific product**:
```bash
python yttrsch.py \
  --keyword "iphone 14" \
  --video https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

3. **Batch mode**: searching multiple videos for a political term:
```bash
python yttrsch.py \
  --keyword "climate change" \
  --file videos.txt
```
Where `videos.txt` contains links like:
```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
```

## Output

The script outputs YouTube video URLs where the keyword was found in the transcript:
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
...
```
If any errors occur during transcript retrieval, they are listed separately after the results.

## Limitations

1. Requires videos to have transcripts enabled  
2. Limited by YouTube API quotas and rate limits  
3. Only searches for exact matches (not semantic search)  
4. Requires YouTube Data API key  
5. May not work with auto-generated transcripts in some languages  
6. Can be time-consuming for channels with many videos  

## Troubleshooting

**Problem**: API key errors  
- **Solution**: Ensure your API key is correctly set in the `.env` file

**Problem**: "Quota exceeded" errors  
- **Solution**: Wait until your daily YouTube API quota resets or use a different API key

**Problem**: Missing transcripts for many videos  
- **Solution**: Some channels may disable transcripts or use formats not supported by the API

**Problem**: Script running slowly  
- **Solution**: This is normal for channels with many videos; transcript retrieval is rate-limited

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a pull request

---

**Disclaimer**: Use this script responsibly and respect YouTube's terms of service. The YouTube API has usage limits, and exceeding them may result in temporary or permanent API access suspension.