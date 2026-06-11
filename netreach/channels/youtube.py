import os
import re
import tempfile
import glob
import yt_dlp

def clean_vtt(vtt_text: str) -> str:
    """Cleans a WebVTT file content to return readable plain text without timestamps."""
    lines = vtt_text.splitlines()
    clean_lines = []
    for line in lines:
        line = line.strip()
        # Skip WebVTT header, metadata, empty lines, and timestamp lines
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        
        # Remove WebVTT formatting tags e.g. <c>, <00:00:01.000>
        line = re.sub(r"<[^>]+>", "", line)
        line = line.strip()
        if line:
            clean_lines.append(line)
            
    # Remove consecutive duplicate lines (common in scrolling auto-captions)
    deduped = []
    for line in clean_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
            
    return "\n".join(deduped)

def get_youtube_transcript(url: str) -> dict:
    """Extracts captions from a video, falling back to metadata if subtitles are unavailable."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en"],
                "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            sub_files = glob.glob(os.path.join(tmpdir, "*.vtt")) + glob.glob(os.path.join(tmpdir, "*.srt"))
            
            metadata = {
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "uploader": info.get("uploader", ""),
                "channel_url": info.get("channel_url", ""),
                "duration": info.get("duration", 0),
                "view_count": info.get("view_count", 0),
            }
            
            if sub_files:
                sub_path = sub_files[0]
                with open(sub_path, "r", encoding="utf-8", errors="ignore") as f:
                    vtt_content = f.read()
                transcript = clean_vtt(vtt_content)
                return {
                    "error": False,
                    "type": "transcript",
                    "transcript": transcript,
                    "metadata": metadata
                }
            else:
                return {
                    "error": False,
                    "type": "metadata",
                    "transcript": None,
                    "metadata": metadata,
                    "message": "No English subtitles/transcripts found. Returning video metadata as fallback."
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred extracting transcript: {str(e)}",
            "channel": "youtube",
            "fallback_tried": True
        }

def search_youtube(query: str, limit: int = 5) -> dict:
    """Searches YouTube for videos by keyword query using yt-dlp flat extraction."""
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            entries = info.get("entries", [])
            results = []
            for entry in entries:
                results.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}" if entry.get("id") else entry.get("url"),
                    "uploader": entry.get("uploader"),
                    "duration": entry.get("duration"),
                    "view_count": entry.get("view_count"),
                })
            return {"results": results, "error": False}
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred searching YouTube: {str(e)}",
            "channel": "youtube",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes the YouTube channel by checking if yt-dlp is importable."""
    try:
        version = yt_dlp.version.__version__
        return {
            "ok": True,
            "backend": f"yt-dlp (v{version})",
            "detail": "yt-dlp is installed and available"
        }
    except Exception as e:
        return {
            "ok": False,
            "backend": "yt-dlp",
            "detail": f"Failed to check yt-dlp: {str(e)}"
        }
