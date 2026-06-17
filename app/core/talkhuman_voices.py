PUBLIC_TALKHUMAN_VOICES = [
    {
        "alias": "Superman",
        "display_name": "Superman",
        "style": "bright",
        "description": "Clear, elevated, and optimistic.",
        "private_voice": "Zephyr",
    },
    {
        "alias": "Spider-Man",
        "display_name": "Spider-Man",
        "style": "upbeat",
        "description": "Quick, friendly, and conversational.",
        "private_voice": "Puck",
    },
    {
        "alias": "Batman",
        "display_name": "Batman",
        "style": "informative",
        "description": "Low, focused, and direct.",
        "private_voice": "Charon",
    },
    {
        "alias": "Wonder Woman",
        "display_name": "Wonder Woman",
        "style": "firm",
        "description": "Confident, warm, and grounded.",
        "private_voice": "Kore",
    },
    {
        "alias": "Wolverine",
        "display_name": "Wolverine",
        "style": "excitable",
        "description": "Rugged, energetic, and reactive.",
        "private_voice": "Fenrir",
    },
    {
        "alias": "Captain Marvel",
        "display_name": "Captain Marvel",
        "style": "youthful",
        "description": "Bright, lively, and modern.",
        "private_voice": "Leda",
    },
    {
        "alias": "Thor",
        "display_name": "Thor",
        "style": "firm",
        "description": "Commanding, resonant, and steady.",
        "private_voice": "Orus",
    },
    {
        "alias": "Phoenix",
        "display_name": "Phoenix",
        "style": "breezy",
        "description": "Warm, expressive, and flowing.",
        "private_voice": "Aoede",
    },
    {
        "alias": "Aquaman",
        "display_name": "Aquaman",
        "style": "easygoing",
        "description": "Relaxed, open, and casual.",
        "private_voice": "Callirrhoe",
    },
    {
        "alias": "Ant-Man",
        "display_name": "Ant-Man",
        "style": "bright",
        "description": "Light, agile, and approachable.",
        "private_voice": "Autonoe",
    },
    {
        "alias": "Hulk",
        "display_name": "Hulk",
        "style": "breathy",
        "description": "Heavy, textured, and intense.",
        "private_voice": "Enceladus",
    },
    {
        "alias": "Iron Man",
        "display_name": "Iron Man",
        "style": "clear",
        "description": "Crisp, clever, and polished.",
        "private_voice": "Iapetus",
    },
    {
        "alias": "Nightcrawler",
        "display_name": "Nightcrawler",
        "style": "easygoing",
        "description": "Soft, calm, and nimble.",
        "private_voice": "Umbriel",
    },
    {
        "alias": "Black Panther",
        "display_name": "Black Panther",
        "style": "smooth",
        "description": "Refined, balanced, and poised.",
        "private_voice": "Algieba",
    },
    {
        "alias": "Invisible Woman",
        "display_name": "Invisible Woman",
        "style": "smooth",
        "description": "Gentle, composed, and reassuring.",
        "private_voice": "Despina",
    },
    {
        "alias": "Scarlet Witch",
        "display_name": "Scarlet Witch",
        "style": "clear",
        "description": "Precise, expressive, and controlled.",
        "private_voice": "Erinome",
    },
    {
        "alias": "Green Lantern",
        "display_name": "Green Lantern",
        "style": "gravelly",
        "description": "Strong, textured, and serious.",
        "private_voice": "Algenib",
    },
    {
        "alias": "Doctor Strange",
        "display_name": "Doctor Strange",
        "style": "informative",
        "description": "Measured, articulate, and thoughtful.",
        "private_voice": "Rasalgethi",
    },
    {
        "alias": "Storm",
        "display_name": "Storm",
        "style": "upbeat",
        "description": "Lifted, confident, and vivid.",
        "private_voice": "Laomedeia",
    },
    {
        "alias": "Flash",
        "display_name": "Flash",
        "style": "soft",
        "description": "Fast, light, and gentle.",
        "private_voice": "Achernar",
    },
    {
        "alias": "Captain America",
        "display_name": "Captain America",
        "style": "firm",
        "description": "Reliable, centered, and earnest.",
        "private_voice": "Alnilam",
    },
    {
        "alias": "Star-Lord",
        "display_name": "Star-Lord",
        "style": "even",
        "description": "Balanced, casual, and steady.",
        "private_voice": "Schedar",
    },
    {
        "alias": "Daredevil",
        "display_name": "Daredevil",
        "style": "mature",
        "description": "Grounded, serious, and mature.",
        "private_voice": "Gacrux",
    },
    {
        "alias": "Supergirl",
        "display_name": "Supergirl",
        "style": "forward",
        "description": "Confident, bright, and present.",
        "private_voice": "Pulcherrima",
    },
    {
        "alias": "Hawkeye",
        "display_name": "Hawkeye",
        "style": "friendly",
        "description": "Dry, clear, and personable.",
        "private_voice": "Achird",
    },
    {
        "alias": "Martian Manhunter",
        "display_name": "Martian Manhunter",
        "style": "casual",
        "description": "Thoughtful, calm, and approachable.",
        "private_voice": "Zubenelgenubi",
    },
    {
        "alias": "Vision",
        "display_name": "Vision",
        "style": "gentle",
        "description": "Even, precise, and gentle.",
        "private_voice": "Vindemiatrix",
    },
    {
        "alias": "Robin",
        "display_name": "Robin",
        "style": "lively",
        "description": "Young, responsive, and lively.",
        "private_voice": "Sadachbia",
    },
    {
        "alias": "Cyborg",
        "display_name": "Cyborg",
        "style": "knowledgeable",
        "description": "Technical, concise, and controlled.",
        "private_voice": "Sadaltager",
    },
    {
        "alias": "Shazam",
        "display_name": "Shazam",
        "style": "warm",
        "description": "Warm, friendly, and animated.",
        "private_voice": "Sulafat",
    },
]


def _normalize_voice_name(voice_name: str) -> str:
    return voice_name.strip().casefold()


def list_public_talkhuman_voices() -> list[dict]:
    return [
        {
            "alias": voice["alias"],
            "display_name": voice["display_name"],
            "style": voice["style"],
            "description": voice["description"],
        }
        for voice in PUBLIC_TALKHUMAN_VOICES
    ]


def resolve_talkhuman_voice(voice_name: str) -> dict:
    normalized = _normalize_voice_name(voice_name)
    for voice in PUBLIC_TALKHUMAN_VOICES:
        if normalized in {
            _normalize_voice_name(voice["alias"]),
            _normalize_voice_name(voice["display_name"]),
            _normalize_voice_name(voice["private_voice"]),
        }:
            return voice

    raise ValueError(f"Unknown Eburon AI voice alias: {voice_name}")

