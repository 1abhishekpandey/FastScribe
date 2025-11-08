# Future Scope

## Auto-Download + Whisper Fallback

Enable automatic video download (via yt-dlp) when YouTube subtitles are unavailable, then transcribe with Whisper. Seamless experience, requires additional dependency.

**Benefits:**
- One-step workflow for any YouTube video
- No manual download needed
- Automatic fallback handling

**Requirements:**
- Add `yt-dlp` to dependencies
- Video download to `input/` folder
- Auto-trigger Whisper transcription
