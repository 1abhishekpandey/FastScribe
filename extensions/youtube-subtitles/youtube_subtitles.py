"""
YouTube Subtitle Extraction Module

This module provides functionality to extract subtitles directly from YouTube videos
without transcription, using the youtube-transcript-api.
"""

import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


def extract_video_id(url):
    """
    Extract video ID from various YouTube URL formats.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID

    Args:
        url (str): YouTube URL

    Returns:
        str: Video ID or None if invalid
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_available_languages(video_id):
    """
    Get list of available subtitle languages for a video.

    Args:
        video_id (str): YouTube video ID

    Returns:
        list: List of available language codes
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        languages = []

        # Get all available transcripts (manual and auto-generated)
        for transcript in transcript_list:
            languages.append(transcript.language_code)

        return languages
    except Exception as e:
        return []


def fetch_transcript(video_id, language='en'):
    """
    Fetch transcript for a YouTube video in specified language.

    Args:
        video_id (str): YouTube video ID
        language (str): Language code (e.g., 'en', 'hi', 'auto')

    Returns:
        list: List of transcript segments with text, start, and duration

    Raises:
        TranscriptsDisabled: If subtitles are disabled for the video
        NoTranscriptFound: If requested language is not available
        VideoUnavailable: If video doesn't exist or is private
    """
    try:
        api = YouTubeTranscriptApi()

        if language == 'auto':
            # Get the first available transcript
            transcript_list = api.list(video_id)
            # Try to find auto-generated English or Hindi
            try:
                transcript = transcript_list.find_generated_transcript(['en', 'hi'])
            except:
                # If no auto-generated, get the first available
                transcript = next(iter(transcript_list))

            fetched = transcript.fetch()
            # Convert FetchedTranscript to list of dicts
            return [{'text': entry.text, 'start': entry.start, 'duration': entry.duration}
                   for entry in fetched]
        else:
            # Get specific language transcript
            fetched = api.fetch(video_id, languages=[language])
            # Convert FetchedTranscript to list of dicts
            return [{'text': entry.text, 'start': entry.start, 'duration': entry.duration}
                   for entry in fetched]
    except TranscriptsDisabled:
        raise Exception(f"Subtitles are disabled for this video (ID: {video_id})")
    except NoTranscriptFound:
        available_langs = get_available_languages(video_id)
        if available_langs:
            raise Exception(
                f"No transcript found for language '{language}'. "
                f"Available languages: {', '.join(available_langs)}"
            )
        else:
            raise Exception(f"No transcripts available for this video (ID: {video_id})")
    except VideoUnavailable:
        raise Exception(f"Video is unavailable or doesn't exist (ID: {video_id})")


def format_as_text(transcript):
    """
    Format transcript as plain text.

    Args:
        transcript (list): List of transcript segments

    Returns:
        str: Formatted plain text transcript
    """
    text_lines = []

    for entry in transcript:
        text = entry['text'].strip()
        if text:
            text_lines.append(text)

    return ' '.join(text_lines)


def save_transcript(text, output_path):
    """
    Save transcript text to file.

    Args:
        text (str): Transcript text
        output_path (str): Output file path
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)


def extract_subtitles(youtube_url, output_dir='output', language='en'):
    """
    Extract subtitles from YouTube video and save as text file.

    Args:
        youtube_url (str): YouTube video URL
        output_dir (str): Directory to save output file
        language (str): Language code ('en', 'hi', 'auto')

    Returns:
        str: Path to saved transcript file

    Raises:
        ValueError: If URL is invalid
        Exception: If subtitle extraction fails
    """
    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {youtube_url}")

    # Fetch transcript
    transcript = fetch_transcript(video_id, language)

    # Format as text
    text = format_as_text(transcript)

    # Generate output filename
    output_filename = f"{video_id}_transcript.txt"
    output_path = os.path.join(output_dir, output_filename)

    # Save transcript
    save_transcript(text, output_path)

    return output_path
