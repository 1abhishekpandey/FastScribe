# YouTube Subtitles Extension - Claude Code Reference

Quick reference for the YouTube subtitle extraction extension.

## What It Is

Extension that extracts existing captions from YouTube videos without transcription. Instant results when videos have captions.

## Quick Usage

```bash
# Basic extraction (English)
python3 extensions/youtube-subtitles/youtube_subs.py <youtube-url> --lang en

# Check available languages
python3 extensions/youtube-subtitles/youtube_subs.py <youtube-url> --list-languages

# Auto-detect language
python3 extensions/youtube-subtitles/youtube_subs.py <youtube-url> --lang auto
```

## File Structure

```
extensions/youtube-subtitles/
├── CLAUDE.md              # This file
├── youtube_subs.py        # CLI entry point
└── youtube_subtitles.py   # Core extraction module
```

## Core Module Functions

**youtube_subtitles.py:**
- `extract_video_id(url)` - Extracts video ID from YouTube URLs
- `get_available_languages(video_id)` - Lists available subtitle languages
- `fetch_transcript(video_id, language)` - Fetches transcript from YouTube
- `format_as_text(transcript)` - Converts to plain text
- `save_transcript(text, output_path)` - Saves to file
- `extract_subtitles(youtube_url, output_dir, language)` - Main function

## CLI Options

```bash
python3 extensions/youtube-subtitles/youtube_subs.py <url> [options]

Required:
  url                 YouTube video URL

Optional:
  --lang LANG         Language code (en, hi, auto) [default: en]
  --output DIR        Output directory [default: output/]
  --list-languages    List available subtitle languages
```

## Common Languages

- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `auto` - Auto-detect (first available)

## Output

- Saves as plain text `.txt` files
- Location: `output/` directory (or custom via `--output`)
- Naming: `{VIDEO_ID}_transcript.txt`

## Dependency

```bash
# Install (one-time)
source .venv/bin/activate
pip install youtube-transcript-api
```

Already added to `scripts/requirements.txt`

## When to Use

**Use this extension when:**
- Video already has captions (check with `--list-languages`)
- Need instant results (no processing time)
- Want to avoid Whisper transcription overhead

**Use main FastScribe when:**
- No subtitles available on YouTube
- Need higher accuracy than auto-generated captions
- Processing local video files

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| "No subtitles available" | Video has no captions | Use FastScribe Whisper transcription |
| "No transcript found for language 'XX'" | Language not available | Use `--list-languages` to check available |
| "Invalid YouTube URL" | URL format incorrect | Use standard YouTube URL formats |

## Example Workflow

```bash
# 1. Check what's available
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --list-languages

# 2. Extract if available
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang en

# 3. If no subs, fall back to Whisper
# Download video, place in input/, then:
python3 transcribe.py --default
```

## Full Documentation

See `docs/youtube-subtitles.md` for complete documentation.
