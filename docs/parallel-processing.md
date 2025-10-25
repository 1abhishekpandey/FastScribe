# FastScribe - Parallel Processing Guide

This document explains how FastScribe uses parallel processing to speed up transcription.

## Overview

Instead of processing an entire video sequentially, the tool splits it into smaller chunks and transcribes them simultaneously using multiple CPU cores. This can provide **2-4x speedup** depending on your hardware.

## How It Works

### 1. Video Splitting
- FFmpeg splits the input video into equal-sized chunks
- Chunks are saved as temporary video files in `.temp_chunks/`
- Split happens very quickly (usually under 5 seconds)

### 2. Parallel Transcription
- Each chunk is assigned to a separate Python process
- Processes run simultaneously using `ProcessPoolExecutor`
- Each process runs its own instance of Whisper AI model

### 3. Progress Tracking
- Each chunk reports progress via JSON files
- Main process reads these files and displays coordinated progress bars
- You see real-time progress for all chunks simultaneously

### 4. Results Merging
- Completed transcripts are concatenated in order
- Temporary chunk files are automatically cleaned up
- Final transcript saved to `output/` folder

## Performance Guidelines

### Choosing Thread Count

The number of threads determines how many chunks your video is split into.

| Threads | RAM Required | Typical Speedup | Best For |
|---------|--------------|-----------------|----------|
| 1 | 2-4 GB | 1x (no speedup) | Low-end systems |
| 2 | 4-8 GB | 1.5-2x | **Default - most systems** |
| 4 | 8-16 GB | 2-3x | Modern laptops/desktops |
| 8 | 16-32 GB | 3-4x | High-end workstations |

**Recommendation**: Start with 2 threads and increase if you have sufficient RAM.

### Memory Considerations

Each parallel process loads the entire Whisper model into memory:

- **tiny** model: ~400 MB per process
- **base** model: ~1 GB per process
- **small** model: ~2 GB per process
- **medium** model: ~5 GB per process
- **large** model: ~10 GB per process

**Example**: Running 4 threads with medium model requires ~20 GB RAM (5 GB × 4).

### CPU Considerations

Parallel processing benefits from:
- **Multiple CPU cores** (4+ cores recommended for 4 threads)
- **Fast single-core performance** (Whisper is CPU-intensive)
- **Modern CPUs** (2018 or newer recommended)

## Usage Examples

### Quick Start (Defaults)
```bash
python3 transcribe.py --default
```
Uses 2 threads - good for most systems.

### High Performance
```bash
python3 transcribe.py --threads 4 --model 3
```
4 threads with small model - fast and accurate.

### Maximum Speed
```bash
python3 transcribe.py --threads 8 --model 1
```
8 threads with tiny model - fastest possible (lower accuracy).

### Maximum Accuracy
```bash
python3 transcribe.py --threads 2 --model 5
```
2 threads with large model - best accuracy (very slow).

## Real-World Performance

Based on a 30-minute video with base model:

| Configuration | Time | Speedup | RAM Used |
|---------------|------|---------|----------|
| 1 thread | ~12 min | 1x | ~2 GB |
| 2 threads | ~6 min | 2x | ~4 GB |
| 4 threads | ~4 min | 3x | ~8 GB |
| 8 threads | ~3 min | 4x | ~16 GB |

*Performance varies by CPU speed and video content.*

## Progress Display Explained

While transcribing, you'll see:

```
Starting parallel transcription of 4 chunks...

Chunk 1:  75%|███████████████████| [01:30<00:30]
Chunk 2:  68%|█████████████████  | [01:25<00:35]
Chunk 3:  82%|████████████████████| [01:35<00:20]
Chunk 4:  71%|██████████████████ | [01:28<00:32]
```

Each line shows:
- **Chunk number**: Which chunk is being processed
- **Percentage**: How much of that chunk is complete
- **Progress bar**: Visual representation
- **Time elapsed**: How long this chunk has been processing
- **Time remaining**: Estimated time to complete this chunk

## Technical Details

### Process Staggering
To avoid overwhelming the system at startup:
- Processes start with a 2% stagger delay
- If chunk 1 is at 2%, chunk 2 starts
- If chunk 2 is at 2%, chunk 3 starts
- And so on...

This prevents all processes from loading the model simultaneously.

### Inter-Process Communication
- Each process writes progress to a JSON file
- Main process polls these files every 0.5 seconds
- Uses `tqdm` for smooth progress bar rendering

### Error Handling
- If any chunk fails, the entire process stops
- Partial transcripts are not saved
- Temporary files are cleaned up even on failure

## Limitations

### Fixed Chunk Size
Chunks are split by time duration (equal sized), not by content. This means:
- A sentence might be split across chunks
- Transcription might have minor inconsistencies at chunk boundaries

### Memory Overhead
Each process loads the full model, which can use significant RAM with larger models.

### No GPU Support
Currently uses CPU only. GPU support may be added in the future.

## Troubleshooting

### Out of Memory Errors
**Problem**: System runs out of RAM during transcription.

**Solutions**:
- Reduce thread count: `--threads 2`
- Use smaller model: `--model 1` (tiny) or `--model 2` (base)
- Close other applications
- Process videos one at a time

### Slow Performance
**Problem**: Parallel processing isn't faster than expected.

**Solutions**:
- Increase threads if you have RAM: `--threads 4`
- Use faster model: `--model 1` or `--model 2`
- Check CPU usage (should be near 100% across all cores)
- Ensure video is on fast storage (SSD better than HDD)

### Inconsistent Progress
**Problem**: Progress bars jump around or freeze.

**Explanation**: This is normal. Whisper processes audio in variable-sized segments, so progress isn't perfectly linear.

## Advanced Configuration

For developers who want to modify parallel processing behavior, see:
- `scripts/transcribe_parallel.py:VideoTranscriber` - Main class
- `scripts/transcribe_parallel.py:process_chunk()` - Chunk processing function
- `scripts/transcribe_parallel.py:TqdmProgressCapture` - Progress tracking

For full technical details, see [`architecture.md`](architecture.md).

## Summary

Parallel processing is a powerful feature that can significantly reduce transcription time:
- **Default (2 threads)** works for most systems
- **Increase threads** if you have sufficient RAM
- **Balance speed vs accuracy** by choosing appropriate model
- **Monitor progress** in real-time for all chunks

For more information:
- **User Guide**: [`../README.md`](../README.md)
- **Technical Architecture**: [`architecture.md`](architecture.md)
