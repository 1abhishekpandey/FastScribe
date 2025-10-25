# FastScribe - Claude Code Reference

Quick reference for Claude Code AI assistant.

## What It Is

FastScribe is a fast parallel video transcription tool powered by OpenAI Whisper.

## Quick Commands

```bash
# Setup (one-time)
brew install ffmpeg
python3 setup.py

# Run with defaults (English, base model, 2 threads)
python3 transcribe.py --default

# Custom run
python3 transcribe.py --threads 4 --model 3 --lang auto

# Interactive mode (prompts for settings)
python3 transcribe.py
```

## Project Structure

```
FastScribe/
├── setup.py            # One-time setup
├── transcribe.py       # Main entry point
├── LICENSE             # MIT License
├── README.md           # User documentation
├── CLAUDE.md           # This file
├── input/              # Videos go here
├── output/             # Transcripts saved here
├── .venv/              # Python environment (isolated)
├── .temp_chunks/       # Temporary (auto-cleaned)
├── scripts/            # Python code
│   ├── transcribe_parallel.py  # Core transcription engine
│   └── requirements.txt        # Dependencies
└── docs/
    └── architecture.md # Technical details
```

## CLI Options

```bash
--default           # English, base model, 2 threads
--threads N         # Parallel threads (1-N)
--model M           # 1=tiny, 2=base, 3=small, 4=medium, 5=large
--lang LANG         # en=English, hi=Hindi, auto=Auto-detect
```

## Available Languages

- **English** (default)
- **Hindi**
- **Auto-detect** (Whisper detects automatically)

## Models

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| base | 140 MB | Fast | **Default - recommended** |
| medium | 1.4 GB | Slow | High accuracy needed |
| large | 2.9 GB | Slowest | Maximum accuracy |

## Common Issues

| Issue | Fix |
|-------|-----|
| "No video files found" | Put files in `input/` folder |
| "ModuleNotFoundError" | Run `python3 setup.py` |
| "ffmpeg not found" | Run `brew install ffmpeg` |
| Virtual env issues | `rm -rf .venv && python3 setup.py` |

## Key Technical Points

- Parallel processing via `ProcessPoolExecutor`
- Custom progress tracking via `TqdmProgressCapture`
- Inter-process communication via JSON files
- FFmpeg for video splitting (parallelized)
- Dynamic process staggering (2% threshold)

**For detailed architecture, see:** `docs/architecture.md`

## Typical User Workflow

1. Place videos in `input/`
2. Run `python3 transcribe.py --default`
3. Watch progress bars
4. Find transcripts in `output/`

## Notes

- Videos split into chunks and processed in parallel
- Language selection appears first in interactive mode
- Auto-detect lets Whisper choose the language
- All dependencies isolated in `.venv/`
- Models cached globally in `~/.cache/whisper/`
