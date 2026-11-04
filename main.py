import os, json, time, random, asyncio, subprocess, urllib.parse
import requests, feedparser
import edge_tts
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# الإعدادات العامة ورابط الربح الخاص بك
# ==========================================
AFFILIATE_LINK = "https://www.youtube.com/@Unfold1-t3w?sub_confirmation=1"
LANGUAGES = ["en", "es", "de", "fr", "pt", "ar", "hi", "ja", "ko"]
HISTORY_FILE = "history.json"

# مكتبة كل أنواع محتوى الـ AI البصرية
AI_STYLES = {
    "3d_simulation": "3D medical and physics simulation style like Zack D Films, glossy 3D render, cross-section view, clean studio lighting, Unreal Engine 5, ultra-detailed 8k",
    "pixar_cartoon": "3D Pixar Disney animation style, expressive cute 3D cartoon characters, vibrant colors, volumetric cinematic lighting, Unreal Engine 5 render, 8k",
    "dark_cinema": "Hyper-realistic Netflix dark documentary cinematography, 35mm lens, moody dramatic lighting, shallow depth of field, photorealistic 8k",
    "sci_fi_future": "Futuristic cinematic sci-fi concept art, holographic neon lighting, photorealistic CGI, IMAX 70mm quality, 8k",
    "epic_anime": "High-budget Makoto Shinkai anime movie style, breathtaking detailed background, dramatic lighting, vibrant cinematic colors, 8k"
}

# مكتبة الأصوات الاحترافية حسب جو الفيديو
VOICES = {
    "dramatic": "en-US-ChristopherNeural",
    "energetic": "en-US-GuyNeural",
    "storyteller": "en-US-AriaNeural"
}

# ==========================================
# 1. صيد الترند الحقيقي يومياً
# ==========================================
def get_daily_trend():
    history = json.load(open(HISTORY_FILE, encoding="utf-8")) if os.path.exists(HISTORY_FILE) else []
    feeds = [
        "https://trends.google.com/trending/rss?geo=US",
        "https://www.reddit.com/r/todayilearned/top/.rss?t=day",
        "https://www.reddit.com/r/Damnthatsinteresting/top/.rss?t=day"
    ]
    trends = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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

# ==========================================
# 2. المخرج الذكي (السكريبت، الكاميرا، الـ 9 لغات، والتعليق المثبت)
# ==========================================
def generate_content(trends):
    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    prompt = f"""
    Pick the most viral, curiosity-inducing topic from this list: {trends}.
    Act as an elite YouTube AI Director. Your goal is maximum viewer retention (never boring!) and high CTR.
    1. Choose the best visual style for each scene from: ["3d_simulation", "pixar_cartoon", "dark_cinema", "sci_fi_future", "epic_anime"].
    2. Choose the narrator mood from: ["dramatic", "energetic", "storyteller"].
    3. Design a consistent 'character_dna' so any recurring character or subject looks identical across scenes.
    4. Vary 'camera_move' across scenes using: ["zoom_in", "zoom_out", "pan_right", "pan_left"].
    5. Generate SEO Titles, Descriptions, Pinned Comment CTAs, and Subtitles in all 9 languages: {LANGUAGES}.

    Return STRICT JSON in this exact format:
    {{
      "selected_topic": "topic name",
      "voice_mood": "dramatic",
      "character_dna": "Detailed visual description of main character or core subject",
      "thumbnail_prompt": "Extreme close-up viral YouTube thumbnail, high contrast, expressive shocked face or glowing 3D cross-section, 8k, no text",
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
          "pinned_comment": "Want to try the #1 AI tool we used today? Check it out here:",
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
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    res = requests.post(url, json=payload, timeout=180)
    res.raise_for_status()
    data = json.loads(res.json()["candidates"][0]["content"]["parts"][0]["text"])

    char_dna = data.get("character_dna", "")
    for scene in data["long_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}. {char_dna}, {scene['action_prompt']}, no text, no watermark"

    for scene in data["short_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}. {char_dna}, {scene['action_prompt']}, vertical 9:16 composition, no text"

    return data

# ==========================================
# 3. توليد الصوتيات والصور (Flux AI)
# ==========================================
async def create_voice(text, filename, mood="dramatic"):
    voice_name = VOICES.get(mood, "en-US-ChristopherNeural")
    communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
    await communicate.save(filename)

def download_image(prompt, width, height, filename, seed=42):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&nologo=true&seed={seed}"
    for _ in range(3):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(filename, "wb") as f:
                    f.write(r.content)
                return
        except Exception:
            time.sleep(3)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d=1", "-frames:v", "1", filename])

def get_audio_duration(filename):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename]
    return float(subprocess.check_output(cmd).decode().strip())

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

# ==========================================
# 4. المونتاج السينمائي وحركات الكاميرا (FFmpeg)
# ==========================================
def get_camera_filter(move, width, height, frames, fps):
    base = f"scale={width*2}:{height*2},zoompan="
    if move == "zoom_out":
        return f"{base}z='if(eq(on,1),1.45,max(1.001,zoom-0.0025))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif move == "pan_right":
        return f"{base}z=1.25:d={frames}:x='min(iw-iw/zoom,(on/{frames})*(iw-iw/zoom))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif move == "pan_left":
        return f"{base}z=1.25:d={frames}:x='max(0,(1-on/{frames})*(iw-iw/zoom))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    else:
        return f"{base}z='min(zoom+0.0025,1.45)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

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
        download_image(scene["image_prompt"], width, height, img_path, seed=video_seed)
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
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_video])

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

# ==========================================
# 5. النشر الشامل (9 لغات + صورة مصغرة + ترجمات + أول تعليق بالرابط)
# ==========================================
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

    # تجهيز العناوين والأوصاف مع وضع الرابط المثبت في أول سطر لكل لغة
    loc_payload = {}
    for lang in LANGUAGES:
        lang_data = localizations.get(lang, localizations["en"])
        t = lang_data["title"]
        if is_short and "#Shorts" not in t:
            t = f"{t[:85]} #Shorts"
        cta = lang_data.get("pinned_comment", "Check this out:")
        full_desc = f"🔥 {cta} {AFFILIATE_LINK}\n\n{lang_data['description']}\n\n#AI #3D #Animation #Viral"
        loc_payload[lang] = {"title": t[:100], "description": full_desc[:4900]}

    body = {
        "snippet": {
            "title": loc_payload["en"]["title"],
            "description": loc_payload["en"]["description"],
            "tags": data.get("tags", ["AI", "3D", "Documentary", "Shorts"]),
            "defaultLanguage": "en",
            "categoryId": "24"
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        "localizations": loc_payload
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media)
    res = req.execute()
    video_id = res["id"]
    print(f"Uploaded {'Short' if is_short else 'Long'} Video ID: {video_id}")

    # 1. رفع الصورة المصغرة (Thumbnail) للفيديو الطويل
    if not is_short and thumb_path and os.path.exists(thumb_path):
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_path)).execute()
        except Exception as e:
            print(f"Thumbnail skip (Verify YT phone number if needed): {e}")

    # 2. نشر التعليق الأول (الرابط المثبت) تلقائياً تحت الفيديو
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

    # 3. رفع ملفات الترجمة (CC) للغات الـ 9 للفيديو الطويل
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

    # توليد صورة مصغرة جذابة للفيديو الطويل
    thumb_file = "thumbnail.jpg"
    download_image(
        f"{AI_STYLES['3d_simulation']}, {data.get('thumbnail_prompt', data['selected_topic'])}, vibrant high contrast, no text",
        1280, 720, thumb_file, seed=777
    )

    # صناعة الفيديو الطويل (16:9) والفيديو القصير (9:16)
    long_vid, long_srts = build_video(data["long_scenes"], "long", 1280, 720, data["localizations"], "long_subs", mood)
    short_vid, short_srts = build_video(data["short_scenes"], "short", 720, 1280, data["localizations"], "short_subs", mood)

    # الرفع الشامل إلى يوتيوب
    upload_to_youtube(long_vid, data, long_srts, thumb_path=thumb_file, is_short=False)
    upload_to_youtube(short_vid, data, short_srts, thumb_path=None, is_short=True)

    # حفظ الموضوع في السجل لعدم تكراره مستقبلاً
    history.append(data["selected_topic"])
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
