# YouTube Subtitle Extraction

Extract subtitles directly from YouTube videos without transcription. This is much faster and more cost-effective when videos already have captions.

## Overview

The YouTube subtitle extraction module downloads existing subtitles from YouTube videos and saves them as plain text files. This is ideal when:
- The video already has captions (auto-generated or manual)
- You need instant results without processing time
- You want to avoid transcription costs

## Setup

### One-time Installation

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Install the YouTube transcript API:**
   ```bash
   pip install youtube-transcript-api
   ```

   Or install all dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

## Usage

### Basic Command

```bash
python3 extensions/youtube-subtitles/youtube_subs.py <youtube-url> --lang <language>
```

### Examples

**Extract English subtitles:**
```bash
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang en
```

**Extract Hindi subtitles:**
```bash
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang hi
```

**Auto-detect language:**
```bash
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang auto
```

**Check available languages:**
```bash
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --list-languages
```

**Custom output directory:**
```bash
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang en --output my_transcripts
```

### Supported URL Formats

All standard YouTube URL formats are supported:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Output

- Transcripts are saved as plain text (`.txt`) files
- Default location: `output/` directory
- File naming: `{VIDEO_ID}_transcript.txt`
- Format: Plain text with spaces between sentences

## Language Codes

Common language codes:
- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `ko` - Korean
- `auto` - Auto-detect (uses first available)

## Command-line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | YouTube video URL (required) | - |
| `--lang LANG` | Subtitle language code | `en` |
| `--output DIR` | Output directory | `output/` |
| `--list-languages` | List available languages | - |

## Error Handling

### Common Errors

**"No subtitles available for this video"**
- The video has no captions (auto-generated or manual)
- Solution: Use FastScribe's Whisper transcription instead

**"No transcript found for language 'XX'"**
- The requested language is not available
- Solution: Use `--list-languages` to see available options

**"Invalid YouTube URL"**
- The URL format is incorrect
- Solution: Use standard YouTube URL formats

## Comparison with Whisper Transcription

| Feature | YouTube Subtitles | Whisper Transcription |
|---------|------------------|----------------------|
| Speed | Instant | Minutes to hours |
| Cost | Free | GPU/CPU intensive |
| Accuracy | Varies (auto-gen vs manual) | High |
| Availability | Only if captions exist | Any video file |
| Language Support | Available captions only | 99+ languages |

## Integration with FastScribe

Use YouTube subtitle extraction when:
1. You need quick results
2. The video has existing captions
3. You want to check if transcription is needed

Fall back to FastScribe's Whisper transcription when:
1. No subtitles are available
2. Higher accuracy is required
3. Processing local video files

## Example Workflow

```bash
# 1. Check if subtitles are available
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --list-languages

# 2. If available, extract subtitles
python3 extensions/youtube-subtitles/youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang en

# 3. If not available, download video and use FastScribe
# (Download video using yt-dlp or similar tool)
python3 transcribe.py --default
```

## Technical Details

- **Library:** youtube-transcript-api
- **Method:** Direct API access to YouTube's caption data
- **Output Format:** Plain text (.txt)
- **Processing:** No video download or audio processing required
