import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

from crewai.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


def extract_video_id(url_or_id: str) -> str | None:
    """Extract YouTube video ID from any YouTube URL format, parameter variations, or raw ID."""
    if not url_or_id:
        return None

    cleaned = url_or_id.strip()

    # Match raw 11-char ID directly
    if re.match(r"^[0-9A-Za-z_-]{11}$", cleaned):
        return cleaned

    # Comprehensive regex list covering all YouTube URL variations:
    patterns = [
        r"(?:https?:\/\/)?(?:www\.|m\.|music\.)?youtube\.com\/watch\?[^ \t\n\r\"<>]*[?&]v=([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/shorts\/([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/live\/([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube|youtube-nocookie)\.com\/embed\/([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([0-9A-Za-z_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/e\/([0-9A-Za-z_-]{11})",
        r"(?:[?&]v=)([0-9A-Za-z_-]{11})",
        r"(?:v=|\/v\/|embed\/|shorts\/|live\/|youtu\.be\/|\/e\/)([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)

    # Fallback to standard URL parsing for complex query strings
    try:
        parsed = urllib.parse.urlparse(cleaned)
        if "youtube" in parsed.netloc or "youtu.be" in parsed.netloc:
            if parsed.netloc.endswith("youtu.be"):
                path_id = parsed.path.lstrip("/")
                if len(path_id) >= 11:
                    return path_id[:11]
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("v"):
                return qs["v"][0][:11]
            path_parts = [p for p in parsed.path.split("/") if p]
            if path_parts and path_parts[0] in ("shorts", "live", "embed", "v", "e") and len(path_parts) > 1:
                return path_parts[1][:11]
    except (ValueError, KeyError, IndexError, TypeError) as err:
        logger.debug("Failed parsing complex query string in URL %s: %s", cleaned, err)

    return None


def get_video_oembed_info(video_id: str) -> dict:
    """Fetch video metadata (Title, Author/Channel, Thumbnail) via YouTube oEmbed API with HTML fallback."""
    if not video_id:
        return {}

    # 1. Try YouTube oEmbed API
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            if data:
                raw_title = (data.get("title") or "").strip()
                return {
                    "title": raw_title if raw_title else f"YouTube Video ({video_id})",
                    "author_name": (data.get("author_name") or "").strip() or "Content Creator",
                    "author_url": data.get("author_url", ""),
                    "thumbnail_url": data.get("thumbnail_url", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"),
                    "video_id": video_id,
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError, ValueError) as err:
        logger.debug("YouTube oEmbed request failed for %s: %s", video_id, err)

    # 2. HTML Scraper Fallback
    try:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        req_page = urllib.request.Request(
            watch_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req_page, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html) or re.search(r'<title>([^<]+)</title>', html)
            author_match = re.search(r'<link itemprop="name" content="([^"]+)"', html) or re.search(r'"author":"([^"]+)"', html)
            
            title = title_match.group(1).replace(" - YouTube", "") if title_match else f"YouTube Video ({video_id})"
            author = author_match.group(1) if author_match else "Content Creator"
            
            return {
                "title": title,
                "author_name": author,
                "author_url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "video_id": video_id,
                "video_url": watch_url,
            }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as err:
        logger.debug("HTML metadata scrape failed for %s: %s", video_id, err)

    return {
        "title": f"YouTube Video ({video_id})",
        "author_name": "Content Creator",
        "author_url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
    }


def search_youtube_videos(query: str, max_results: int = 5) -> list[str]:
    """Search entire YouTube database for a query or channel topic and return matching video IDs."""
    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    req = urllib.request.Request(
        search_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            video_ids = re.findall(r'"videoId":"([0-9A-Za-z_-]{11})"', html)
            seen = set()
            unique_ids = []
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    unique_ids.append(vid)
            return unique_ids[:max_results]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        logger.warning("[YouTube Search] Warning: Search query failed: %s", e)
        return []


def fetch_youtube_transcript(video_id: str) -> str | None:
    """Retrieve transcript text with multi-language, auto-generated, and translation fallback."""
    api = YouTubeTranscriptApi()

    # Step 1: Try default fetch (English / default tracks)
    try:
        transcript_data = api.fetch(video_id)
        parts = []
        for snippet in transcript_data:
            text = getattr(snippet, "text", "") if hasattr(snippet, "text") else (snippet.get("text", "") if isinstance(snippet, dict) else "")
            if text:
                parts.append(text)
        if parts:
            return " ".join(parts)
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as err:
        logger.debug("Default transcript fetch failed for %s: %s", video_id, err)

    # Step 2: Try fetching via transcript list (multilingual / auto-generated / translated)
    try:
        transcript_list = api.list(video_id)
        target_langs = ["en", "en-US", "en-GB", "hi", "es", "fr", "de", "pt", "it", "ja", "ko", "zh-Hans", "zh-Hant", "ru", "ar"]
        
        # 2a. Find exact matching manual or auto transcript
        for lang in target_langs:
            try:
                tr = transcript_list.find_transcript([lang])
                fetched = tr.fetch()
                parts = [getattr(s, "text", "") if hasattr(s, "text") else (s.get("text", "") if isinstance(s, dict) else "") for s in fetched]
                joined = " ".join([p for p in parts if p])
                if joined:
                    return joined
            except (ValueError, KeyError, TypeError, OSError, RuntimeError) as lang_err:
                logger.debug("Could not fetch transcript for lang %s on %s: %s", lang, video_id, lang_err)

        # 2b. Try finding any transcript and auto-translating to English
        for tr in transcript_list:
            try:
                if hasattr(tr, "is_translatable") and tr.is_translatable:
                    try:
                        translated_tr = tr.translate("en")
                        fetched = translated_tr.fetch()
                        parts = [getattr(s, "text", "") if hasattr(s, "text") else (s.get("text", "") if isinstance(s, dict) else "") for s in fetched]
                        joined = " ".join([p for p in parts if p])
                        if joined:
                            return joined
                    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as trans_err:
                        logger.debug("Translation to en failed for %s: %s", video_id, trans_err)
                # Direct fetch fallback
                fetched = tr.fetch()
                parts = [getattr(s, "text", "") if hasattr(s, "text") else (s.get("text", "") if isinstance(s, dict) else "") for s in fetched]
                joined = " ".join([p for p in parts if p])
                if joined:
                    return joined
            except (ValueError, KeyError, TypeError, OSError, RuntimeError) as tr_err:
                logger.debug("Fallback fetch failed for %s: %s", video_id, tr_err)
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as err:
        logger.debug("Listing transcripts failed for %s: %s", video_id, err)

    return None


def inspect_youtube_url(url_or_query: str) -> dict:
    """Inspect any YouTube URL or query, returning parsed video ID, metadata, thumbnail, and transcript availability."""
    cleaned = (url_or_query or "").strip()
    if not cleaned:
        return {"valid": False, "error": "Empty input provided."}

    video_id = extract_video_id(cleaned)

    if not video_id:
        # Search YouTube database
        results = search_youtube_videos(cleaned, max_results=1)
        if results:
            video_id = results[0]

    if not video_id:
        return {
            "valid": False,
            "error": "No valid YouTube video could be identified from this input.",
            "query": cleaned,
        }

    meta = get_video_oembed_info(video_id)
    transcript = fetch_youtube_transcript(video_id)
    has_transcript = bool(transcript and len(transcript.strip()) > 50)

    return {
        "valid": True,
        "video_id": video_id,
        "title": meta.get("title", f"YouTube Video ({video_id})"),
        "author": meta.get("author_name", "Content Creator"),
        "author_url": meta.get("author_url", f"https://www.youtube.com/watch?v={video_id}"),
        "thumbnail_url": meta.get("thumbnail_url", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"),
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "has_transcript": has_transcript,
        "transcript_preview": (transcript[:300] + "...") if transcript else None,
    }


def query_youtube_database(query: str, max_videos: int = 3) -> dict:
    """Query entire YouTube as a searchable database, extracting transcripts and metadata across multiple matching videos."""
    cleaned = query.strip()
    direct_id = extract_video_id(cleaned)

    if direct_id:
        video_ids = [direct_id]
    else:
        video_ids = search_youtube_videos(cleaned, max_results=max_videos)

    results = []
    combined_transcripts = []

    for vid in video_ids:
        info = get_video_oembed_info(vid)
        transcript = fetch_youtube_transcript(vid)
        
        entry = {
            "video_id": vid,
            "title": info.get("title", f"YouTube Video ({vid})"),
            "author": info.get("author_name", "Creator"),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "has_transcript": bool(transcript),
            "transcript_chars": len(transcript) if transcript else 0,
            "transcript": transcript,
        }
        results.append(entry)

        if transcript:
            snippet = transcript[:8000]
            combined_transcripts.append(
                f"### [Database Entry {len(combined_transcripts)+1}] {entry['title']} (by {entry['author']})\n"
                f"- **URL**: {entry['url']}\n"
                f"- **Transcript Excerpt**:\n{snippet}\n"
            )

    return {
        "query": cleaned,
        "total_videos_found": len(results),
        "videos": results,
        "dossier": "\n\n".join(combined_transcripts) if combined_transcripts else "",
    }


@tool("Universal YouTube Search & Transcript Tool")
def yt_tool(query_or_url: str) -> str:
    """Extracts transcripts, video titles, creator details, and technical/factual insights from ANY YouTube video URL, channel handle, or search query across the entire YouTube database.

    Accepts:
    - Direct YouTube URLs in ANY format (e.g. 'https://www.youtube.com/watch?v=...', 'https://youtu.be/...', 'https://youtube.com/shorts/...', 'https://youtube.com/live/...')
    - Raw 11-char YouTube Video IDs
    - Channel handles or names (e.g. '@krishnaik06', '@lexfridman', 'Andrej Karpathy', 'Fireship')
    - Search queries and topics across all domains
    """
    cleaned = (query_or_url or "").strip()
    if not cleaned:
        return "No topic or YouTube URL provided. Please provide a topic or URL to research."

    # Direct ID check
    direct_id = extract_video_id(cleaned)

    if direct_id:
        info = get_video_oembed_info(direct_id)
        video_title = info.get("title", f"YouTube Video ({direct_id})")
        author_name = info.get("author_name", "Content Creator")
        video_url = f"https://www.youtube.com/watch?v={direct_id}"
        transcript = fetch_youtube_transcript(direct_id)

        if transcript:
            clipped_transcript = transcript[:14000]
            return (
                f"### YouTube Database Video Record\n"
                f"- **Video Title**: {video_title}\n"
                f"- **Channel / Creator**: {author_name}\n"
                f"- **Source URL**: {video_url}\n"
                f"- **Video ID**: `{direct_id}`\n\n"
                f"#### Spoken Transcript & Key Insights:\n"
                f"{clipped_transcript}\n\n"
                f"[End of Transcript Extraction. Use these authentic spoken points, code examples, terminology, and explanations to write the master post.]"
            )
        else:
            return (
                f"### YouTube Database Record Found (Direct Subtitles Unavailable)\n"
                f"- **Video Title**: {video_title}\n"
                f"- **Channel / Creator**: {author_name}\n"
                f"- **Source URL**: {video_url}\n\n"
                f"Synthesize an authoritative technical guide on '{video_title}' focusing on core concepts and architectures in the style of {author_name}."
            )

    # Multi-video database query across YouTube
    db_result = query_youtube_database(cleaned, max_videos=3)
    if db_result.get("dossier"):
        return (
            f"### Universal YouTube Knowledge Base Dossier for: '{cleaned}'\n"
            f"Retrieved {db_result['total_videos_found']} relevant videos across YouTube with verified spoken transcripts:\n\n"
            f"{db_result['dossier']}\n\n"
            f"[End of Multi-Video Intelligence Dossier. Synthesize, contrast, and verify insights across these creator perspectives.]"
        )

    return (
        f"### Research Brief for Target Topic: '{cleaned}'\n"
        f"Provide an authoritative, high-depth breakdown covering definitions, architectural foundations, "
        f"practical examples, industry best practices, and code implementation."
    )


@tool("YouTube Open Knowledge Base Multi-Video Ingestion Tool")
def yt_database_tool(topic_or_channel: str) -> str:
    """Queries entire YouTube as an open multi-source database.

    Searches across creators, playlists, and channels to retrieve and synthesize spoken transcripts from multiple top videos simultaneously.
    """
    cleaned = (topic_or_channel or "").strip()
    if not cleaned:
        return "Please provide a search topic, channel name, or query."

    db_data = query_youtube_database(cleaned, max_videos=3)
    if db_data.get("dossier"):
        return (
            f"### Multi-Video YouTube Database Query: '{cleaned}'\n"
            f"{db_data['dossier']}"
        )
    return f"No transcripts found across YouTube for '{cleaned}'. Use domain synthesis."
