#!/usr/bin/env python3
"""
YouTube Subtitle Extractor

Extract subtitles directly from YouTube videos without transcription.
Subtitles are saved as plain text files in the output/ directory.

Usage:
    python3 youtube_subs.py <youtube-url> --lang en
    python3 youtube_subs.py <youtube-url> --lang hi
    python3 youtube_subs.py <youtube-url> --lang auto

Examples:
    python3 youtube_subs.py https://www.youtube.com/watch?v=dQw4w9WgXcQ --lang en
    python3 youtube_subs.py https://youtu.be/dQw4w9WgXcQ --lang hi
"""

import sys
import argparse
import os

from youtube_subtitles import extract_subtitles, get_available_languages, extract_video_id


def main():
    parser = argparse.ArgumentParser(
        description='Extract subtitles from YouTube videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 youtube_subs.py https://www.youtube.com/watch?v=VIDEO_ID --lang en
  python3 youtube_subs.py https://youtu.be/VIDEO_ID --lang hi
  python3 youtube_subs.py https://youtu.be/VIDEO_ID --lang auto

Supported Languages:
  en    - English
  hi    - Hindi
  auto  - Auto-detect (uses first available)
        """
    )

    parser.add_argument(
        'url',
        help='YouTube video URL'
    )

    parser.add_argument(
        '--lang',
        default='en',
        help='Subtitle language (default: en). Use "auto" for auto-detection.'
    )

    parser.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output/)'
    )

    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List available subtitle languages for the video'
    )

    args = parser.parse_args()

    # Extract video ID for display
    video_id = extract_video_id(args.url)
    if not video_id:
        print(f"Error: Invalid YouTube URL: {args.url}")
        print("Expected formats:")
        print("  - https://www.youtube.com/watch?v=VIDEO_ID")
        print("  - https://youtu.be/VIDEO_ID")
        sys.exit(1)

    # List available languages if requested
    if args.list_languages:
        print(f"Fetching available languages for video: {video_id}...")
        languages = get_available_languages(video_id)
        if languages:
            print(f"\nAvailable subtitle languages:")
            for lang in languages:
                print(f"  - {lang}")
        else:
            print(f"\nNo subtitles available for this video.")
        sys.exit(0)

    # Extract subtitles
    print(f"Extracting subtitles from YouTube video: {video_id}")
    print(f"Language: {args.lang}")
    print(f"Output directory: {args.output}/")
    print()

    try:
        output_path = extract_subtitles(
            youtube_url=args.url,
            output_dir=args.output,
            language=args.lang
        )

        print(f"Success! Subtitles saved to: {output_path}")
        print()

        # Show file stats
        file_size = os.path.getsize(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            word_count = len(content.split())

        print(f"File size: {file_size:,} bytes")
        print(f"Word count: {word_count:,}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Tip: Use --list-languages to see available subtitle languages")
        sys.exit(1)


if __name__ == '__main__':
    main()
