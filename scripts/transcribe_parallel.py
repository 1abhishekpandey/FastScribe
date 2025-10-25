#!/usr/bin/env python3

"""
FastScribe - Parallel Video Transcription Engine
Core transcription logic with parallel chunk processing.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import json
import tempfile
import time
import re
import argparse
import threading
import whisper
from tqdm import tqdm

# Force unbuffered output so progress bars from child processes display properly
os.environ['PYTHONUNBUFFERED'] = '1'

class TqdmProgressCapture(tqdm):
    """Custom tqdm wrapper that captures Whisper's progress and writes to JSON."""

    def __init__(self, *args, progress_file=None, chunk_num=None, **kwargs):
        self.progress_file = progress_file
        self.chunk_num = chunk_num
        # Redirect file to devnull to suppress terminal output, but keep tqdm functional
        import io
        kwargs['file'] = io.StringIO()
        super().__init__(*args, **kwargs)
        # Write initial state
        self._write_progress()

    def update(self, n=1):
        """Override update to capture progress."""
        # Manually update self.n since parent class won't due to StringIO redirection
        self.n = min(self.n + n, self.total) if self.total else self.n + n
        # Write progress to JSON
        self._write_progress()
        return True

    def close(self):
        """Override close to capture final progress."""
        result = super().close()
        self._write_progress()
        return result

    def _write_progress(self):
        """Write current progress to JSON file."""
        if self.progress_file and self.total:
            progress_data = {
                "chunk": self.chunk_num,
                "current": int(self.n),
                "total": int(self.total),
                "percent": int((self.n / self.total * 100) if self.total > 0 else 0),
                "status": "transcribing"
            }
            try:
                with open(self.progress_file, 'w') as f:
                    json.dump(progress_data, f)
            except:
                pass


def transcribe_chunk(chunk_num, chunk_file, output_dir, model_size="base", lang_code="en", temp_dir=None):
    """
    Transcribe a single video chunk (runs in separate process).
    Each process loads its own Whisper model instance.
    Writes real Whisper progress to JSON file for monitoring.
    """
    try:
        # Suppress warnings from Whisper
        import warnings
        warnings.filterwarnings('ignore')

        # Redirect both stdout and stderr to suppress Whisper's terminal output
        import io
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        # Set up progress file
        progress_file = None
        if temp_dir:
            progress_file = Path(temp_dir) / f"progress_chunk_{chunk_num}.json"

        def write_progress(current, total, status="running"):
            """Write progress to JSON file."""
            if progress_file:
                progress_data = {
                    "chunk": chunk_num,
                    "current": current,
                    "total": total,
                    "percent": int((current / total * 100) if total > 0 else 0),
                    "status": status
                }
                try:
                    with open(progress_file, 'w') as f:
                        json.dump(progress_data, f)
                except:
                    pass

        write_progress(0, 1, "starting")

        # Stagger model loading by waiting for previous chunk to reach 2% progress
        if chunk_num > 1 and temp_dir:
            import time as time_module
            previous_chunk_progress = temp_dir / f"progress_chunk_{chunk_num - 1}.json"

            # Wait for previous chunk to reach 2% before starting
            while True:
                if previous_chunk_progress.exists():
                    try:
                        with open(previous_chunk_progress, 'r') as f:
                            prev_data = json.load(f)
                            prev_percent = prev_data.get("percent", 0)
                            if prev_percent >= 2:
                                break  # Previous chunk is at 2%, we can start
                    except:
                        pass
                time_module.sleep(0.5)  # Check every 0.5 seconds

        # Load model in this process FIRST (before patching)
        write_progress(0, 1, "loading_model")
        model = whisper.load_model(model_size)
        write_progress(0, 1, "model_loaded")

        # NOW patch tqdm globally in sys.modules (after model is loaded)
        import tqdm as tqdm_module
        original_tqdm_class = tqdm_module.tqdm

        # Create a wrapper class that returns our custom tqdm
        def create_custom_tqdm(*args, **kwargs):
            """Replace tqdm with our custom version that captures progress."""
            kwargs['progress_file'] = progress_file
            kwargs['chunk_num'] = chunk_num
            return TqdmProgressCapture(*args, **kwargs)

        # Patch tqdm globally
        tqdm_module.tqdm = create_custom_tqdm
        sys.modules['tqdm'].tqdm = create_custom_tqdm

        # Transcribe with verbose=True to enable progress tracking
        # Pass None for language if auto-detect is requested
        whisper_lang = None if lang_code == "auto" else lang_code
        result = model.transcribe(
            str(chunk_file),
            language=whisper_lang,
            verbose=True,  # Enable Whisper's progress (will be captured by our custom tqdm)
            fp16=False  # Disable FP16 since it's not supported on CPU
        )

        write_progress(1, 1, "transcribed")

        # Save transcription
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"chunk_{chunk_num}.txt"
        with open(output_file, 'w') as f:
            for segment in result.get("segments", []):
                text = segment.get("text", "").strip()
                if text:
                    f.write(text + "\n")

        write_progress(1, 1, "complete")

        # Restore stdout, stderr and tqdm
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        tqdm_module.tqdm = original_tqdm_class
        sys.modules['tqdm'].tqdm = original_tqdm_class
        return (chunk_num, True, None)
    except Exception as e:
        # Restore stdout, stderr and tqdm in case of error
        try:
            if 'original_stdout' in locals():
                sys.stdout = original_stdout
            if 'original_stderr' in locals():
                sys.stderr = original_stderr
            if 'original_tqdm_class' in locals():
                import tqdm as tqdm_module
                tqdm_module.tqdm = original_tqdm_class
                sys.modules['tqdm'].tqdm = original_tqdm_class
        except:
            pass
        return (chunk_num, False, str(e))

class VideoTranscriber:
    def __init__(self, max_threads=1, model_size="base", lang_code="en"):
        self.script_dir = Path(__file__).parent.parent.absolute()  # Go up to Transcriptions folder
        self.input_dir = self.script_dir / "input"
        self.output_dir = self.script_dir / "output"
        self.temp_dir = self.script_dir / ".temp_chunks"
        self.max_threads = max_threads
        self.num_chunk_threads = max_threads
        self.lang_code = lang_code
        # Map language codes to readable names
        self.language_names = {
            "en": "English",
            "hi": "Hindi",
            "auto": "Auto-detect"
        }
        self.language = self.language_names.get(lang_code, lang_code.upper())
        self.cleanup = True
        self.model_size = model_size

        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)
        print(f"✓ Model loaded successfully")
        print()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_video_duration(self, video_path):
        """Get video duration in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            duration_str = result.stdout.strip()
            if duration_str and duration_str != "N/A":
                return float(duration_str)
            return None
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None

    def split_video_into_chunks(self, video_path, num_chunks):
        """Split video into chunks using parallel FFmpeg processes."""
        duration = self.get_video_duration(video_path)

        if duration is None:
            print(f"Error: Could not determine video duration. Make sure FFmpeg is installed.")
            return False

        chunk_duration = duration / num_chunks

        print(f"Video Duration: {duration:.0f} seconds")
        print(f"Chunk Duration: {chunk_duration:.0f} seconds")
        print()

        # Clean and create temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        print(f"Splitting video into {num_chunks} chunks...")

        # Helper function to create a single chunk
        def create_chunk(chunk_index):
            """Create a single video chunk using FFmpeg."""
            start_time = (chunk_index - 1) * chunk_duration
            chunk_output = self.temp_dir / f"chunk_{chunk_index}.mp4"

            if chunk_index == num_chunks:
                # Last chunk: no duration limit
                cmd = [
                    "ffmpeg", "-i", str(video_path),
                    "-ss", str(start_time),
                    "-c", "copy", "-y",
                    str(chunk_output)
                ]
            else:
                cmd = [
                    "ffmpeg", "-i", str(video_path),
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-c", "copy", "-y",
                    str(chunk_output)
                ]

            try:
                subprocess.run(cmd, capture_output=True, timeout=300)
                return (chunk_index, True, None)
            except Exception as e:
                return (chunk_index, False, str(e))

        # Create all chunks in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            futures = {executor.submit(create_chunk, i): i for i in range(1, num_chunks + 1)}

            # Collect results
            for future in as_completed(futures):
                chunk_num, success, error = future.result()
                if not success:
                    print(f"Error creating chunk {chunk_num}: {error}")
                    return False

        # Verify chunks
        print("Verifying chunks...")
        for i in range(1, num_chunks + 1):
            chunk_file = self.temp_dir / f"chunk_{i}.mp4"
            if chunk_file.exists():
                chunk_dur = self.get_video_duration(chunk_file)
                if chunk_dur:
                    print(f"  ✓ Chunk {i} created: {chunk_dur:.0f} seconds")
                else:
                    print(f"  ✗ Chunk {i} duration unknown")
            else:
                print(f"  ✗ Chunk {i} missing!")
                return False

        print("✓ Video splitting complete")
        print()
        return True


    def process_video(self, video_path, current, total):
        """Process a single video file."""
        video_name = video_path.name
        name_no_ext = video_path.stem
        num_chunks = self.num_chunk_threads

        print("=" * 50)
        print(f"File {current}/{total}: {video_name}")
        print(f"Language: {self.language}")
        print(f"Processing with {num_chunks} parallel jobs")
        print("=" * 50)
        print()

        # Split video (now parallelized internally with ThreadPoolExecutor)
        if not self.split_video_into_chunks(video_path, num_chunks):
            print(f"Failed to split video: {video_name}")
            return False

        # Transcribe chunks in parallel using ProcessPoolExecutor
        print(f"Starting parallel transcription of {num_chunks} chunks...")
        print()

        results = {}

        # Start monitoring thread for progress display
        progress_bars = {}
        stop_monitor = threading.Event()

        def monitor_progress():
            """Monitor progress files and display percentage-based progress bars."""
            import time as time_module

            # Initialize progress bars (100% scale)
            for i in range(1, num_chunks + 1):
                progress_bars[i] = tqdm(
                    total=100,
                    desc=f"Chunk {i}",
                    position=i-1,
                    leave=True,
                    unit="%",
                    bar_format='{desc}: {percentage:3.0f}%|{bar}| [{elapsed}<{remaining}]'
                )

            last_percent = {i: 0 for i in range(1, num_chunks + 1)}

            # Continue reading until all chunks complete
            while True:
                all_done = True

                for i in range(1, num_chunks + 1):
                    progress_file = self.temp_dir / f"progress_chunk_{i}.json"

                    if progress_file.exists():
                        try:
                            with open(progress_file, 'r') as f:
                                data = json.load(f)
                                percent = data.get("percent", 0)
                                status = data.get("status", "running")

                                # Update progress bar with percentage
                                if percent > last_percent[i]:
                                    delta = percent - last_percent[i]
                                    progress_bars[i].update(delta)
                                    last_percent[i] = percent

                                if status != "complete":
                                    all_done = False
                        except:
                            pass
                    else:
                        all_done = False

                # Exit only when stop_monitor is set AND all chunks are complete
                if stop_monitor.is_set() and all_done:
                    break

                time_module.sleep(0.5)

            # Close all progress bars
            for bar in progress_bars.values():
                bar.close()

        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()

        executor = ProcessPoolExecutor(max_workers=self.num_chunk_threads)
        try:
            futures = {}

            # Submit all chunks for transcription
            for i in range(1, num_chunks + 1):
                chunk_file = self.temp_dir / f"chunk_{i}.mp4"
                output_dir = self.temp_dir / f"output_chunk_{i}"

                future = executor.submit(
                    transcribe_chunk,
                    i,
                    chunk_file,
                    output_dir,
                    self.model_size,
                    self.lang_code,
                    self.temp_dir  # Pass temp_dir for progress file writing
                )
                futures[future] = i

            # Collect results as chunks complete (progress bars display above)
            for future in as_completed(futures):
                chunk_num, success, error = future.result()
                results[chunk_num] = (success, error)

        except KeyboardInterrupt:
            print("\n\n⚠️  Transcription interrupted by user (Ctrl+C)")
            print("Cleaning up processes...")

            # Stop monitoring thread
            stop_monitor.set()
            monitor_thread.join(timeout=1)

            # Shutdown executor and terminate all running processes
            executor.shutdown(wait=False, cancel_futures=True)

            # Clean up temp chunks directory
            if self.temp_dir.exists():
                print("Removing temporary files...")
                shutil.rmtree(self.temp_dir)

            print("✓ Cleanup complete")
            return False

        finally:
            # Ensure executor is always closed
            executor.shutdown(wait=True)

        # Stop monitoring thread
        stop_monitor.set()
        monitor_thread.join(timeout=2)

        # Check for errors
        failed = {n: e for n, (s, e) in results.items() if not s}
        if failed:
            print()
            print("⚠️  Some chunks failed:")
            for chunk_num, error in failed.items():
                print(f"  Chunk {chunk_num}: {error}")
            print()

        print()
        print("Combining transcripts...")

        # Combine transcripts
        final_transcript = self.output_dir / f"{name_no_ext}.txt"
        with open(final_transcript, 'w') as outfile:
            for i in range(1, num_chunks + 1):
                chunk_transcript = self.temp_dir / f"output_chunk_{i}" / f"chunk_{i}.txt"
                if chunk_transcript.exists():
                    with open(chunk_transcript, 'r') as infile:
                        outfile.write(infile.read())
                else:
                    print(f"Warning: Transcript for chunk {i} not found")

        print("✓ Transcription complete!")
        print(f"Output: {final_transcript}")
        print()

        # Cleanup
        if self.cleanup:
            print("Cleaning up temporary chunks...")
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            print("✓ Cleanup complete")
        else:
            print(f"Note: Temporary chunks saved in: {self.temp_dir}")
            print(f"To clean up later, run: rm -rf \"{self.temp_dir}\"")

        print()
        return True

    def run(self):
        """Main execution method."""
        print("=" * 50)
        print("Parallel Transcription Script (Python)")
        print(f"Background Threads: {self.max_threads}")
        print(f"Whisper Model: {self.model_size}")
        print(f"Language: {self.language}")
        print("=" * 50)
        print()

        print(f"Cleanup: Auto-cleanup enabled")
        print()

        # Find video files
        video_files = sorted(self.input_dir.glob("*.mp4"))

        if not video_files:
            print(f"No video files found in {self.input_dir}")
            return

        print(f"Found {len(video_files)} video files")
        print(f"Starting background transcription ({self.max_threads} thread{'s' if self.max_threads > 1 else ''})...")
        print()

        # Process videos in background threads
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(self.process_video, video_path, current, len(video_files)): current
                for current, video_path in enumerate(video_files, 1)
            }

            # Wait for all tasks to complete
            for future in as_completed(futures):
                video_num = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing video {video_num}: {e}")

        print("=" * 50)
        print("All transcriptions complete!")
        print(f"Output saved to: {self.output_dir}")
        print("=" * 50)

def main():
    """Entry point."""
    valid_models = ["tiny", "base", "small", "medium", "large"]
    valid_languages = {"en": "English", "hi": "Hindi", "auto": "Auto-detect"}

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Parallel video transcriber using Whisper")
    parser.add_argument("--default", action="store_true", help="Use default settings (English, base model, 2 threads)")
    parser.add_argument("--threads", type=int, default=1, help="Number of parallel threads (default: 1)")
    parser.add_argument("--model", type=int, default=2, choices=[1, 2, 3, 4, 5],
                        help="Whisper model (1=tiny, 2=base, 3=small, 4=medium, 5=large, default: 2)")
    parser.add_argument("--lang", type=str, default="en", choices=["en", "hi", "auto"],
                        help="Language (en=English, hi=Hindi, auto=Auto-detect, default: en)")
    args = parser.parse_args()

    print("=" * 50)
    print("Parallel Video Transcriber Configuration")
    print("=" * 50)
    print()

    if args.default:
        # Use defaults: English, base model, 2 threads
        max_threads = 2
        model_size = "base"
        lang_code = "en"
        print("Using default settings: English, Model: base, Threads: 2")
        print()
    else:
        # Interactive language selection (asked first)
        print("Available languages:")
        print("1) English [DEFAULT]")
        print("2) Hindi")
        print("3) Auto-detect")
        print()
        while True:
            lang_choice = input("Select language (1-3, default: 1): ").strip()
            if not lang_choice:
                lang_code = "en"
                break
            try:
                lang_idx = int(lang_choice)
                if lang_idx == 1:
                    lang_code = "en"
                    break
                elif lang_idx == 2:
                    lang_code = "hi"
                    break
                elif lang_idx == 3:
                    lang_code = "auto"
                    break
                else:
                    print("Error: Please enter 1, 2, or 3")
            except ValueError:
                print("Error: Please enter a valid number")

        print()

        # Interactive thread selection
        while True:
            try:
                threads_input = input("Number of parallel threads (default: 1): ").strip()
                if not threads_input:
                    max_threads = 1
                    break
                max_threads = int(threads_input)
                if max_threads < 1:
                    print("Error: Thread count must be >= 1")
                    continue
                break
            except ValueError:
                print(f"Error: Please enter a valid number")

        print()

        # Interactive model selection
        print("Available Whisper models:")
        model_info = {
            "tiny": "Fastest (low accuracy) - ~39M parameters",
            "base": "Fast (good accuracy) - ~74M parameters [DEFAULT]",
            "small": "Balanced (high accuracy) - ~244M parameters",
            "medium": "Accurate (very high accuracy) - ~769M parameters",
            "large": "Most accurate (slowest) - ~1.5B parameters"
        }

        for i, (model, info) in enumerate(model_info.items(), 1):
            print(f"{i}) {model.capitalize():8} - {info}")

        print()
        while True:
            model_choice = input("Select model (1-5, default: 2): ").strip()
            if not model_choice:
                model_size = "base"
                break
            try:
                choice_idx = int(model_choice) - 1
                if 0 <= choice_idx < len(valid_models):
                    model_size = valid_models[choice_idx]
                    break
                else:
                    print("Error: Please enter a number between 1 and 5")
            except ValueError:
                print("Error: Please enter a valid number")

        print()

    transcriber = VideoTranscriber(max_threads=max_threads, model_size=model_size, lang_code=lang_code)
    transcriber.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Exit silently, let outer script handle the message
        sys.exit(130)  # Standard exit code for Ctrl+C
