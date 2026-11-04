import google.generativeai as genai

def generate_content(trends):
    api_key = os.environ["GEMINI_API_KEY"].strip()
    genai.configure(api_key=api_key)
    
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

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw_text = response.text

    cleaned = raw_text.strip()
    if "```" in cleaned:
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}") + 1
    data = json.loads(cleaned[start_idx:end_idx])

    char_dna = data.get("character_dna", "")
    for scene in data["long_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}. {char_dna}, {scene['action_prompt']}, no text, no watermark"

    for scene in data["short_scenes"]:
        st = AI_STYLES.get(scene.get("style", "3d_simulation"), AI_STYLES["3d_simulation"])
        scene["image_prompt"] = f"{st}. {char_dna}, {scene['action_prompt']}, vertical 9:16 composition, no text"

    return data
