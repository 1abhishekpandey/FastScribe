# FastScribe

Fast parallel video-to-text transcription powered by OpenAI's Whisper AI.

## Features

✓ **Fast Parallel Processing** - Split videos into chunks for 2-4x faster transcription

✓ **Real-Time Progress** - See actual transcription progress for all parallel processes

✓ **Multiple Languages** - English, Hindi, or auto-detect

✓ **Multiple Models** - Choose from 5 Whisper models (speed vs accuracy)

✓ **Many Formats** - Supports mp4, mov, avi, mkv, mp3, wav, m4a, flac, and more

✓ **Isolated Environment** - All dependencies in `.venv/` folder

✓ **Clean Uninstall** - Remove everything by deleting `.venv/` folder

## Quick Start

```bash
# 1. Install FFmpeg (one-time)
brew install ffmpeg

# 2. Set up Python environment (creates input/ and output/ folders)
python3 setup.py

# 3. Place your video files in the input/ folder

# 4. Transcribe your videos
python3 transcribe.py --default
```

Done! Find your transcripts in the `output/` folder as `.txt` files.

**Note**: The setup script automatically creates `input/` and `output/` folders for you.

## Requirements

- macOS (or Linux/Windows with modifications)
- Python 3.9+
- FFmpeg
- 4-8 GB RAM recommended

## Installation

### 1. Install FFmpeg

```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 2. Set Up Python Environment

```bash
python3 setup.py
```

This creates:
- `.venv/` folder with all Python packages isolated from your system
- `input/` folder where you'll place your videos
- `output/` folder where transcripts will be saved

## Usage

### Basic Usage

```bash
python3 transcribe.py --default
```

Uses defaults: English, base model, 2 parallel threads.

### Custom Settings

```bash
# 4 threads, medium model, Hindi
python3 transcribe.py --threads 4 --model 4 --lang hi

# Auto-detect language
python3 transcribe.py --lang auto

# Interactive mode (prompts for all settings)
python3 transcribe.py
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--default` | Use defaults (English, base model, 2 threads) | `--default` |
| `--threads N` | Number of parallel chunks (1-8) | `--threads 4` |
| `--model M` | Whisper model (1-5) | `--model 3` |
| `--lang LANG` | Language (en, hi, auto) | `--lang auto` |

### Languages

| Option | Language | Behavior |
|--------|----------|----------|
| `en` | English | **Default** - Forces English |
| `hi` | Hindi | Forces Hindi |
| `auto` | Auto-detect | Whisper detects language automatically |

### Whisper Models

| # | Model | Size | Speed | Accuracy | Use Case |
|---|-------|------|-------|----------|----------|
| 1 | tiny | 40 MB | Fastest | Low | Quick tests |
| 2 | base | 140 MB | Fast | Good | **Default - balanced** |
| 3 | small | 470 MB | Medium | High | Better accuracy |
| 4 | medium | 1.4 GB | Slow | Very High | High quality needed |
| 5 | large | 2.9 GB | Slowest | Best | Maximum accuracy |

**Recommendation**: Start with **base** model. Upgrade to **medium** if accuracy is insufficient.

## Workflow

1. **Place videos** in `input/` folder
2. **Run** `python3 transcribe.py --default`
3. **Watch** coordinated progress bars for each chunk
4. **Find transcripts** in `output/` folder as `.txt` files

### Progress Display

While transcribing, you'll see real-time progress for each chunk:

```
Starting parallel transcription of 2 chunks...

Chunk 1:  75%|███████████████████| [01:30<00:30]
Chunk 2:  68%|█████████████████  | [01:25<00:35]
```

Each chunk shows percentage, time elapsed, and time remaining.

## Supported Formats

**Video**: mp4, mov, avi, mkv, flv, wmv
**Audio**: mp3, wav, m4a, flac, ogg, aac

## Performance Tips

**Parallel Processing:**
- **2 threads**: Good for 8 GB RAM
- **4 threads**: Good for 16 GB RAM
- **8 threads**: Requires 32 GB+ RAM

**Model Selection:**
- **base** model: ~6 min for 30-min video
- **medium** model: ~15 min for 30-min video

**First Run:**
- Whisper downloads models on first use
- Subsequent runs use cached models (much faster)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No video files found" | Place videos in `input/` folder |
| "ModuleNotFoundError: whisper" | Run `python3 setup.py` |
| "ffmpeg: command not found" | Run `brew install ffmpeg` |
| Slow first run | Whisper is downloading model (happens once) |
| Out of memory | Use fewer threads or smaller model |
| Virtual env issues | `rm -rf .venv && python3 setup.py` |

## Uninstallation

### Remove Python Packages

```bash
rm -rf .venv
```

That's it! All Python dependencies removed.

### Remove FFmpeg (Optional)

```bash
brew uninstall ffmpeg
```

## FAQ

**Q: Can I transcribe languages other than English and Hindi?**

A: Yes! Use `--lang auto` and Whisper will auto-detect the language. For best results with a specific language, you can modify the code (see `docs/architecture.md`).

**Q: Can I get timestamps with the transcription?**

A: Not yet. Output is plain text.

**Q: How much faster is parallel processing?**

A: Typically 2-3x faster with 4 chunks on modern CPUs.

**Q: Will this interfere with my other Python projects?**

A: No. All packages are isolated in `.venv/` and don't affect system Python.

## Technical Documentation

For detailed architecture and implementation:
- **Use Cases & Applications**: [`docs/use-cases.md`](docs/use-cases.md) - Real-world applications and AI-powered workflows
- **Parallel Processing**: [`docs/parallel-processing.md`](docs/parallel-processing.md) - How parallel video processing works
- **Technical Details**: [`docs/architecture.md`](docs/architecture.md) - System design and implementation
- **AI Assistant Guide**: [`CLAUDE.md`](CLAUDE.md) - Quick reference for Claude Code

## Contributing

Contributions welcome! See [`docs/architecture.md`](docs/architecture.md) for technical details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [PyTorch](https://pytorch.org/) - Machine learning framework

---

**Need Help?** Check [`docs/architecture.md`](docs/architecture.md) for technical details.

---

**Made with ❤️ by Vibe Coding!**
