<div align="center">

  <img src="ui/mervid-studio.png" alt="MerVid Studio Logo" width="128" height="128" />

  # MerVid Studio

  **High-Fidelity 4K/8K Media Downloader & Real-Debrid Accelerator**

  [![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](#)
  [![Version](https://img.shields.io/badge/Version-v1.0.0-2CF09E.svg?style=flat&labelColor=111113)](#)
  [![License](https://img.shields.io/badge/License-MIT-white.svg)](#)
  [![Developer](https://img.shields.io/badge/Developer-oguxmercan-2CF09E.svg?logo=github)](https://github.com/oguxmercan)

  <p align="center">
    A modern, sleek, and high-performance desktop media studio designed to download DRM-free 4K/8K videos, lossless audio, high-resolution banners/thumbnails, and unrestrict filehosters & torrents with Real-Debrid API integration.
  </p>

</div>

---

## ⚡ Key Highlights

### 1. 🌐 Universal Media Downloader (1000+ Platforms)
- **YouTube**: 4K & 8K 60FPS HDR, Shorts, complete Playlists, and full Channels.
- **Social Media**: Instagram (Reels, Posts, Stories), TikTok (Watermark-free HD), X (Twitter), Facebook, Reddit, Twitch, Vimeo, SoundCloud, and 1000+ streaming sites.
- **Adult Platforms**: Full native resolution support for standard video streaming services.

### 2. 🚀 Real-Debrid Integration (Gigabit Multi-Hoster & Torrents)
- **Unrestricted Speeds**: Remove download limits and wait times on major hosters like **Rapidgator, 1fichier, Mega, Turbobit, Katfile, DDownload**, and more.
- **Cached Torrent & Magnet Streaming**: Instantly download torrent/magnet files at direct multi-megabyte/gigabit HTTP speeds without seeding or P2P torrent client requirements.
- **In-App Account Manager**: Connect your Real-Debrid API token directly in Settings to view account type, active days left, and premium status in real time.

### 3. 🖼️ High-Resolution Banner & Thumbnail Extraction
- **One-Click Quick Banner Download**: Instant button to export original full-resolution `.jpg` artwork.
- **Automatic Companion Cover**: Automatically save cover artwork alongside video/audio files.
- **ID3 & Metadata Embedding**: Directly embeds covers and media metadata into downloaded `.mp3`, `.mp4`, or `.mkv` files.

### 4. 🎛️ Advanced Control & Automation
- **SponsorBlock**: Automatically removes sponsor segments, intros, outros, and promotional interruptions.
- **Embedded Subtitles**: Auto-muxes soft subtitles (English, Turkish, etc.) directly into video containers.
- **Cookie Vault**: Safely import Netscape `cookies.txt` or paste session cookies locally to unlock age-restricted, subscriber-only, or private videos with 100% privacy.
- **Multi-Thread Saturation**: Configurable 4, 8, or 16 multi-channel connections to maximize your fiber bandwidth.

### 5. 🌍 Multi-Language & Auto System Detection (7 Languages)
MerVid Studio automatically detects your operating system language upon launch. If your system language is not in the list, it gracefully defaults to **English**. You can also manually switch languages at any time from the Settings tab without restarting:
- 🇬🇧 / 🇺🇸 **English** (Default / Global)
- 🇹🇷 **Türkçe** (Turkish)
- 🇨🇳 **简体中文** (Simplified Chinese)
- 🇪🇸 **Español** (Spanish)
- 🇩🇪 **Deutsch** (German)
- 🇳🇱 **Nederlands** (Dutch)
- 🇵🇹 / 🇧🇷 **Português** (Portuguese)

---

## 📸 User Interface

- **Minimalist Dark Aesthetics**: Tailored with deep matte backgrounds and `#2CF09E` (Cyber Emerald / Mint) accents.
- **Real-Time Speed & Telemetry**: Dynamic live progress bar, active speed meter, downloaded bytes counter, and smart ETA calculations.
- **History & Queue Management**: Searchable download history with one-click direct play and folder reveal shortcuts.

---

## 🛠️ Quick Start & Installation

### Option 1: Standalone Windows Executable
No Python or dependency installation required! Simply run the pre-built portable executable:
```
dist/MerVid-Studio/MerVid-Studio.exe
```

### Option 2: Running from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oguxmercan/MerVid-Studio.git
   cd MerVid-Studio
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python app.py
   ```

---

## 📦 Building Standalone Executable (.exe)

You can compile a standalone distribution package using the included PyInstaller automation script:

```bash
python build_exe.py
```
The compiled output will be generated in `dist/MerVid-Studio/MerVid-Studio.exe`.

---

## 🤝 Author & Credits

Developed with precision by **[Oğuzhan Mercan](https://github.com/oguxmercan)**.

- Engine: Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) & [pywebview](https://pywebview.flowrl.com/)
- Video Processing: [FFmpeg](https://ffmpeg.org/)
- API: [Real-Debrid REST API](https://real-debrid.com/api)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
