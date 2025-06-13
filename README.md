# 🔨 Side Projects Hub

Welcome to my playground of handy scripts and utilities!
This repository is a collection of my side-projects, tools, and more that I build for solving real-world problems, experimenting with APIs, and learning new things. Browse below for a quick tour, or pick a project and try it out!

---

## 🚀 Projects

### [YouTube Transcript Search Tool (`ytt-search`)](scripts/ytt-search/README.md)
> **What it does:**
Scan YouTube channels, single videos, or a batch of links and search transcripts for your keywords or phrases.
Highlights matches in context, prints jump-to links with timestamps, and shows a slick progress bar!

> **Why:**
I made this tool out of a need to find that one thing someone said in that one 2 hour podcast that I can't find.

👉 [View on GitHub](scripts/ytt-search/README.md)

### [Recursive Web Directory Downloader (`rwdl`)](scripts/rwdl/README.md)
> **What it does:**
Recursively crawl Apache-style web directories and download files matching your extensions (e.g. `.iso`, `.torrent`, `.exe`).
Keeps folder structure intact, skips duplicates, and can resume where it left off.

> **Why:**
I wrote this script because I needed a way to mirror all the .torrent files from the ParrotSec repo into the same versioned folder structure as the original site.

👉 [View on GitHub](scripts/rwdl/README.md)

---

✨ **Coming Soon**
Stay tuned for more utilities file organizers, API wrappers, CLI games, and who knows what else!

---

## 🛠 Installation & Quickstart

1. Clone the repo
```bash
   git clone https://github.com/4ngel2769/side-projects.git
   cd side-projects
   ```

2. Pick a project folder:
   - `scripts/ytt-search`
   - `scripts/rwdl`

3. Create a virtual environment & install requirements
   ```bash
   cd scripts/ytt-search      # or scripts/rwdl
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Configure your credentials (if needed)
   ```bash
   cp .env.example .env
   # edit .env to add your YOUTUBE_API_KEY or other secrets
   ```

5. Run the script!
   ```bash
   python yttrsch.py -k "never,up" -v https://www.youtube.com/watch?v=dQw4w9WgXcQ
   
   python rwdl.py -u https://example.com/files/ -e .iso,.zip
   ```

---

## 💚 Contributing

Your feedback and pull-requests are welcome!
1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

Please follow [Contributing Guidelines and Code of Conduct](CONTRIBUTING.md).

---

## 📄 License

All projects are released under the MIT License.
See [LICENSE](LICENSE) for details.

---

## 📡 Stay Connected

Questions, ideas or just want to say hi?
– [GitHub Issues](https://github.com/4ngel2769/side-projects/issues)
– [Twitter @angeldev0](https://twitter.com/angeldev0)
<!-- – [LinkedIn](https://www.linkedin.com/in/???/) -->
