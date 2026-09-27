"""
Fix broken banner/destination image URLs in the local SQLite database.
This script is resilient to missing `None` values and schema variations.
"""

import json
import urllib.parse
import urllib.request

from database import SessionLocal
import models


# Return a copy with all occurrences of substring old replaced by new.

# count

# Maximum number of occurrences to replace.
# -1 (the default value) means replace all occurrences.

# If the optional argument count is given, only the first count occurrences are replaced.
STATE_BANNERS = {
    "JK": "https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=1200&q=80",
    "HP": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "PB": "https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=1200&q=80",
    "HR": "https://images.unsplash.com/photo-1605152276897-4f618f831968?auto=format&fit=crop&w=1200&q=80",
    "UK": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    "UP": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
    "RJ": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "DL": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
    "GJ": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "MH": "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=1200&q=80",
    "KA": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
    "KL": "https://images.unsplash.com/photo-1593104547489-5cfb3839a3b5?auto=format&fit=crop&w=1200&q=80",
    "WB": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
    "AP": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
    "TG": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80",
    "TN": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
    "AS": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    "AR": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "TR": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
}

WIKIPEDIA_PAGES = {
    "JK": "Tourism in Jammu and Kashmir",
    "PB": "Golden Temple",
    "PY": "Tourism in Puducherry",
}

DEST_IMAGES = {
    "dal lake": "https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=600&q=80",
    "gulmarg": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80",
    "golden temple": "https://images.unsplash.com/photo-1583309219338-a582f1db9a71?auto=format&fit=crop&w=600&q=80",
    "gateway of india": "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=600&q=80",
    "hampi": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=600&q=80",
    "munnar": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80",
    "victoria memorial": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=600&q=80",
    "varanasi": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=600&q=80",
    "taj mahal": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=600&q=80",
    "amber fort": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=600&q=80",
}

FALLBACK_IMG = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=600&q=80"


def get_reference_banner(state):
    state_code = getattr(state, "code", None) or getattr(state, "state_code", None)
    if not state_code:
        return None

    page_name = WIKIPEDIA_PAGES.get(state_code, getattr(state, "name", None) or state_code)
    page_path = urllib.parse.quote(page_name.replace(" ", "_"))
    request = urllib.request.Request(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_path}",
        headers={"User-Agent": "Geonova image audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            summary = json.loads(response.read().decode("utf-8"))
        return summary.get("originalimage", {}).get("source")
    except Exception:
        return None


def get_dest_image(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        return FALLBACK_IMG

    lowered = cleaned.lower()
    for key, url in DEST_IMAGES.items():
        if key in lowered:
            return url
    return FALLBACK_IMG


def fix_images() -> None:
    db = SessionLocal()
    updated_states = 0
    updated_destinations = 0

    try:
        states = db.query(models.StateUT).all()
        for state in states:
            current_banner = getattr(state, "banner_image", None)
            if isinstance(current_banner, str) and "wikimedia.org" in current_banner:
                continue

            state_code = getattr(state, "code", None)
            new_banner = get_reference_banner(state) or STATE_BANNERS.get(state_code)
            if isinstance(new_banner, str) and current_banner != new_banner:
                state.banner_image = new_banner
                updated_states += 1

        destinations = db.query(models.Destination).all()
        for destination in destinations:
            new_image = get_dest_image(getattr(destination, "name", "") or "")
            if getattr(destination, "image_url", None) != new_image:
                destination.image_url = new_image
                updated_destinations += 1

        db.commit()
        print(f"Updated {updated_states} state banner images.")
        print(f"Updated {updated_destinations} destination images.")
        print("Image fix complete.")
    except Exception as exc:
        db.rollback()
        print(f"Error during image fix: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_images()
