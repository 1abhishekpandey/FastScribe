# Changelog

All notable changes to FastScribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-09

### Added

- YouTube URL support in interactive mode for instant subtitle extraction
- Standalone YouTube subtitle extraction extension (`extensions/youtube-subtitles/`)
- Source selection prompt (Input folder vs YouTube URL) in interactive mode
- Language availability checking with `--list-languages` flag
- Auto-detect mode for YouTube subtitles
- Documentation: `docs/youtube-subtitles.md`
- Extension reference: `extensions/youtube-subtitles/CLAUDE.md`
- New dependency: `youtube-transcript-api`

### Fixed

- Hindi language transcription issues

### Changed

- Interactive mode now shows source selection first
- Updated README.md with YouTube workflows
- Updated CLAUDE.md with YouTube integration details

## [1.0.0] - 2025-01-XX

### Added

- Initial release of FastScribe
- Parallel video transcription using OpenAI Whisper
- Support for 5 Whisper models (tiny, base, small, medium, large)
- Multi-language support (English, Hindi, auto-detect)
- Real-time progress tracking for parallel chunks
- Interactive mode with user-friendly prompts
- CLI mode with `--default` flag for quick transcription
- Support for multiple video/audio formats (mp4, mov, avi, mkv, mp3, wav, m4a, flac)
- Configurable thread count (1-8 parallel threads)
- Isolated Python environment with `.venv/`
- Custom TqdmProgressCapture for inter-process progress tracking
- JSON-based IPC for coordinated progress updates
- FFmpeg-powered video splitting
- Documentation: README.md, docs/architecture.md, CLAUDE.md

[1.1.0]: https://github.com/yourusername/fastscribe/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/fastscribe/releases/tag/v1.0.0
