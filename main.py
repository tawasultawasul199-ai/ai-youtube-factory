import os, json, time, random, asyncio, subprocess, urllib.parse
import requests, feedparser
import edge_tts
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

AFFILIATE_LINK = "https://www.youtube.com/@Unfold1-t3w?sub_confirmation=1"
LANGUAGES = ["en", "es", "de", "fr", "pt", "ar", "hi", "ja", "ko"]
HISTORY_FILE = "history.json"

AI_STYLES = {
    "3d_simulation": "2D vector explainer style, minimalist black stickman character, clean line art, solid pastel background, whiteboard style, high quality, vibrant flat colors",
    "pixar_cartoon": "2D vector cartoon explainer style, simple clean lines, flat colors, friendly stickman character, educational aesthetic",
    "dark_cinema": "2D vector minimalist style, clean lines, flat vector art, dramatic storytelling aesthetic",
    "sci_fi_future": "Clean 2D vector technical explainer style, minimalist vector art",
    "epic_anime": "Clean minimalist 2D vector stickman style, flat aesthetic"
}

VOICES = {
    "dramatic": "en-US-ChristopherNeural",
    "energetic": "en-US-GuyNeural",
    "storyteller": "en-US-AriaNeural"
}

def get_daily_trend():
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    feeds = [
        "https://trends.google.com/trending/rss?geo=US",
        "https://www.reddit.com/r/todayilearned/top/.rss?t=day",
        "https://www.reddit.com/r/Damnthatsinteresting/top/.rss?t=day"
    ]
    trends = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in feeds:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(r.content)
            for entry in feed.entries[:15]:
                if entry.title not in history:
                    trends.append(entry.title)
        except Exception:
            pass
    if not trends:
        trends = ["What Happens Inside the Human Body Under Extreme Conditions"]
    return trends[:12], history

def get_candidate_gemini_models(api_key):
    candidates = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(list_url, timeout=30)
        if res.status_code == 200:
            models = res.json().get("models", [])
            excluded = ["vision", "embedding", "imagen", "tts", "audio", "robotics", "computer-use", "aqa", "thinking"]
            for m in models:
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods and "gemini" in name.lower():
                    if not any(x in name.lower() for x in excluded):
                        candidates.append(name)
    except Exception as e:
        print(f"ListModels warning: {e}")

    priority = [
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
        "models/gemini-1.5-flash-latest",
        "models/gemini-pro-latest"
    ]
    ordered = []
    for p in priority:
        if p in candidates and p not in ordered:
            ordered.append(p)
    for c in reversed(candidates):
        if c not in ordered:
            ordered.append(c)
    for p in priority:
        if p not in ordered:
            ordered.append(p)
    return ordered

def parse_ai_json(raw_text):
    cleaned = raw_text.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                cleaned = part
                break
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}") + 1
    return json.loads(cleaned[start_idx:end_idx])

def generate_content(trends):
    api_key = os.environ["GEMINI_API_KEY"].strip()

    prompt = f"""
    Pick the most viral, curiosity-inducing topic from this list: {trends}.
    Act as an elite YouTube AI Director. Your goal is maximum viewer retention and high CTR.
    1. Choose the best visual style for each scene from: ["3d_simulation", "pixar_cartoon", "dark_cinema", "sci_fi_future", "epic_anime"].
    2. Choose the narrator mood from: ["dramatic", "energetic", "storyteller"].
    3. Design a consistent 'character_dna' so any recurring character or subject looks identical across scenes.
    4. Vary 'camera_move' across scenes using: ["zoom_in", "zoom_out", "pan_right", "pan_left"].
    5. Generate SEO Titles, Descriptions, Pinned Comment CTAs, and Subtitles in all 9 languages: {LANGUAGES}.

    Return ONLY valid JSON (no markdown, no backticks) in this exact format:
    {{
      "selected_topic": "topic name",
      "voice_mood": "dramatic",
      "character_dna": "Detailed visual description of stickman character",
      "thumbnail_prompt": "Minimalist 2D vector explainer thumbnail, clean stickman character, vibrant flat colors, no text",
      "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
      "long_scenes": [
        {{
          "style": "3d_simulation",
          "camera_move": "zoom_in",
          "narration_en": "1-2 punchy, thrilling sentences (12-18 words max) to keep fast pacing.",
          "action_prompt": "Specific visual action happening in this scene"
        }}
      ],
      "short_scenes": [
        {{
          "style": "pixar_cartoon",
          "camera_move": "zoom_out",
          "narration_en": "1 ultra-fast hook sentence (10-14 words max).",
          "action_prompt": "Vertical close-up visual action"
        }}
      ],
      "localizations": {{
        "en": {{
          "title": "High-CTR Viral Title (under 70 chars)",
          "description": "3-paragraph engaging SEO description with hashtags",
          "pinned_comment": "Subscribe and check out our official channel here:",
          "long_subs": ["subtitle for scene 1", "..."],
          "short_subs": ["subtitle for short scene 1", "..."]
        }},
        "es": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "de": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "fr": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "pt": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "ar": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "hi": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "ja": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}},
        "ko": {{"title": "...", "description": "...", "pinned_comment": "...", "long_subs": ["..."], "short_subs": ["..."]}}
      }}
    }}
    IMPORTANT: Provide 12 scenes for 'long_scenes' and 6 scenes for 'short_scenes'. Ensure 'long_subs' has 12 items and 'short_subs' has 6 items for every language.
    """

    data = None
    candidate_models = get_candidate_gemini_models(api_key)

    for model_name in candidate_models:
        for version in ["v1beta", "v1"]:
            url = f"https://generativelanguage.googleapis.com/{version}/{model_name}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            try:
                res = requests.post(url, json=payload, timeout=120)
                if res.status_code == 200:
                    raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = parse_ai_json(raw_text)
                    if "long_scenes" in parsed and "short_scenes" in parsed:
                        data = parsed
                        break
            except Exception:
                pass
        if data:
            break

    if not data:
        res = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "openai",
                "jsonMode": True
            },
            timeout=180
        )
        res.raise_for_status()
        data = parse_ai_json(res.text)

    char_dna = data.get("character_dna", "")
    for scene in data["long_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}, stickman character, {char_dna}, {scene['action_prompt']}, clean flat vector style, colorful background, no text"

    for scene in data["short_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}, stickman character, {char_dna}, {scene['action_prompt']}, vertical 9:16 composition, clean flat vector style, no text"

    return data

async def create_voice(text, filename, mood="dramatic"):
    voice_name = VOICES.get(mood, "en-US-ChristopherNeural")
    for _ in range(3):
        try:
            communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
            await communicate.save(filename)
            if os.path.exists(filename) and os.path.getsize(filename) > 100:
                return
        except Exception:
            await asyncio.sleep(2)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "4", "-q:a", "9", "-acodec", "libmp3lame", filename])

def download_image(prompt, width, height, filename, seed=42):
    encoded = urllib.parse.quote(prompt)
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=stable-diffusion&nologo=true&seed={seed}",
        f"https://pollinations.ai/p/{encoded}?width={width}&height={height}&seed={seed}"
    ]
    for url in urls:
        for _ in range(2):
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200 and len(r.content) > 3000:
                    with open(filename, "wb") as f:
                        f.write(r.content)
                    return
            except Exception:
                time.sleep(1)
    
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", 
        "-i", f"color=c=aliceblue:s={width}x{height}:d=1", 
        "-frames:v", "1", filename
    ])

def get_audio_duration(filename):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename]
    return float(subprocess.check_output(cmd).decode().strip())

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def get_camera_filter(move, width, height, frames, fps):
    base = f"scale={width*2}:{height*2},zoompan="
    if move == "zoom_out":
        return f"{base}z='if(eq(on,1),1.35,max(1.001,zoom-0.002))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif move == "pan_right":
        return f"{base}z=1.15:d={frames}:x='min(iw-iw/zoom,(on/{frames})*(iw-iw/zoom))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif move == "pan_left":
        return f"{base}z=1.15:d={frames}:x='max(0,(1-on/{frames})*(iw-iw/zoom))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    else:
        return f"{base}z='min(zoom+0.002,1.35)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

def build_video(scenes, prefix, width, height, localizations, sub_key, mood="dramatic"):
    os.makedirs(prefix, exist_ok=True)
    clip_files = []
    timings = []
    current_time = 0.0
    video_seed = random.randint(100, 99999)

    for i, scene in enumerate(scenes):
        audio_path = f"{prefix}/audio_{i}.mp3"
        img_path = f"{prefix}/img_{i}.jpg"
        clip_path = f"{prefix}/clip_{i}.mp4"

        asyncio.run(create_voice(scene["narration_en"], audio_path, mood))
        download_image(scene["image_prompt"], width, height, img_path, seed=video_seed + i)
        duration = get_audio_duration(audio_path)
        timings.append((current_time, current_time + duration))
        current_time += duration

        fps = 25
        frames = int(duration * fps) + 12
        vf = get_camera_filter(scene.get("camera_move", "zoom_in"), width, height, frames, fps)

        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", audio_path,
            "-vf", vf, "-c:v", "libx264", "-t", str(duration),
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", clip_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(f"file 'clip_{i}.mp4'")

    list_path = f"{prefix}/list.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        f.write("\n".join(clip_files))

    output_video = f"{prefix}_final.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_video], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    srt_files = {}
    for lang in LANGUAGES:
        srt_path = f"{prefix}_{lang}.srt"
        subs = localizations.get(lang, {}).get(sub_key, [])
        with open(srt_path, "w", encoding="utf-8") as f:
            for idx, (start, end) in enumerate(timings):
                text = subs[idx] if idx < len(subs) else scenes[idx]["narration_en"]
                f.write(f"{idx+1}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n")
        srt_files[lang] = srt_path

    return output_video, srt_files

def upload_to_youtube(video_path, data, srt_files, thumb_path=None, is_short=False):
    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"]
    )
    youtube = build("youtube", "v3", credentials=creds)
    localizations = data["localizations"]

    loc_payload = {}
    for lang in LANGUAGES:
        lang_data = localizations.get(lang, localizations["en"])
        t = lang_data["title"]
        if is_short and "#Shorts" not in t:
            t = f"{t[:85]} #Shorts"
        cta = lang_data.get("pinned_comment", "Check this out:")
        full_desc = f"🔥 {cta} {AFFILIATE_LINK}\n\n{lang_data['description']}\n\n#Stickman #Animation #Explainer #Viral"
        loc_payload[lang] = {"title": t[:100], "description": full_desc[:4900]}

    body = {
        "snippet": {
            "title": loc_payload["en"]["title"],
            "description": loc_payload["en"]["description"],
            "tags": data.get("tags", ["Stickman", "Animation", "Explainer", "Shorts"]),
            "defaultLanguage": "en",
            "categoryId": "24"
        },
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
        "localizations": loc_payload
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media)
    res = req.execute()
    video_id = res["id"]
    print(f"Uploaded {'Short' if is_short else 'Long'} Video ID: {video_id}")
    print(f"Direct Studio Link: https://studio.youtube.com/video/{video_id}/edit")

    if not is_short and thumb_path and os.path.exists(thumb_path):
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_path)).execute()
        except Exception as e:
            print(f"Thumbnail skip: {e}")

    try:
        en_cta = localizations["en"].get("pinned_comment", "Check out this link:")
        ar_cta = localizations.get("ar", {}).get("pinned_comment", "اضغط على الرابط التالي:")
        es_cta = localizations.get("es", {}).get("pinned_comment", "Mira este enlace:")
        comment_text = f"📌 {en_cta} {AFFILIATE_LINK}\n🌍 {es_cta} {AFFILIATE_LINK}\n🔥 {ar_cta} {AFFILIATE_LINK}"
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": comment_text}}
                }
            }
        ).execute()
    except Exception as e:
        print(f"Comment skip: {e}")

    if not is_short:
        for lang, srt_path in srt_files.items():
            try:
                youtube.captions().insert(
                    part="snippet",
                    body={"snippet": {"videoId": video_id, "language": lang, "name": lang.upper(), "isDraft": False}},
                    media_body=MediaFileUpload(srt_path)
                ).execute()
            except Exception as e:
                print(f"Subtitle skip {lang}: {e}")

if __name__ == "__main__":
    trends, history = get_daily_trend()
    data = generate_content(trends)
    mood = data.get("voice_mood", "dramatic")

    thumb_file = "thumbnail.jpg"
    download_image(
        f"Minimalist 2D vector explainer thumbnail, clean stickman character, vibrant flat colors, no text",
        1280, 720, thumb_file, seed=777
    )

    long_vid, long_srts = build_video(data["long_scenes"], "long", 1280, 720, data["localizations"], "long_subs", mood)
    short_vid, short_srts = build_video(data["short_scenes"], "short", 720, 1280, data["localizations"], "short_subs", mood)

    upload_to_youtube(long_vid, data, long_srts, thumb_path=thumb_file, is_short=False)
    upload_to_youtube(short_vid, data, short_srts, thumb_path=None, is_short=True)

    history.append(data["selected_topic"])
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
