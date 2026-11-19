import hashlib
import re
import time
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent / "dataset"
HEADERS = {"User-Agent": "sharingan-ai-anmol-26/1.0"}
VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp")

# Main characters: adds 40 new images each (32 train + 8 val)
CHARACTER_SEARCHES = {
    "Luffy": "monkey_d._luffy solo",
    "Naruto": "uzumaki_naruto solo",
    "Ichigo": "kurosaki_ichigo solo",
}

# Random characters for other_unknown: 6 characters x 5 images = 30 images (24 train + 6 val)
OTHER_UNKNOWN_TAGS = [
    "son_goku solo",
    "kamado_tanjirou solo",
    "gojo_satoru solo",
    "roronoa_zoro solo",
    "rem_(re:zero) solo",
    "hatsune_miku solo",
]


def get_existing_state(folder_name):
    """Collect MD5 hashes and highest file number across both train/ and val/."""
    hashes = set()
    max_num = 0
    for split in ("train", "val"):
        folder = BASE_DIR / split / folder_name
        if not folder.exists():
            continue
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() in VALID_EXTS:
                hashes.add(hashlib.md5(f.read_bytes()).hexdigest())
                m = re.search(r"_(\d+)\.", f.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))
    return hashes, max_num


def download_class(folder_name, tags, new_needed=40, new_train_count=32):
    seen_hashes, max_num = get_existing_state(folder_name)
    next_index = max_num + 1
    saved = 0
    pid = 0

    print(f"\nSearching '{tags}' -> {folder_name} (already have {len(seen_hashes)} unique images)...")

    while saved < new_needed:
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "tags": tags,
            "limit": 100,
            "pid": pid,
        }

        response = requests.get("https://safebooru.org/index.php", params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        if not response.text.strip():
            print(f"  No more images found for '{tags}'.")
            break
        posts = response.json()

        if not posts:
            print(f"  No more images found for '{tags}'.")
            break

        for post in posts:
            if saved >= new_needed:
                break

            # Skip if Safebooru's MD5 hash is already in our dataset
            post_hash = post.get("hash")
            if post_hash and post_hash in seen_hashes:
                continue

            img_url = post.get("file_url") or f"https://safebooru.org/images/{post['directory']}/{post['image']}"
            if not img_url.lower().endswith(VALID_EXTS):
                continue

            try:
                img_res = requests.get(img_url, headers=HEADERS, timeout=15)
                img_res.raise_for_status()
                data = img_res.content
            except Exception:
                continue

            img_hash = hashlib.md5(data).hexdigest()
            if img_hash in seen_hashes:
                continue

            split = "train" if saved < new_train_count else "val"
            save_folder = BASE_DIR / split / folder_name
            save_folder.mkdir(parents=True, exist_ok=True)

            ext = Path(img_url).suffix
            file_path = save_folder / f"{folder_name}_{next_index}{ext}"
            file_path.write_bytes(data)

            seen_hashes.add(img_hash)
            saved += 1
            next_index += 1
            print(f"  [{saved}/{new_needed}] Saved {split}/{folder_name}/{file_path.name}")
            time.sleep(0.3)

        pid += 1


if __name__ == "__main__":
    # 1. Add more images to Luffy, Naruto, Ichigo
    for folder, tag_query in CHARACTER_SEARCHES.items():
        download_class(folder, tag_query, new_needed=40, new_train_count=32)

    # 2. Add 30 random anime characters (6 x 5) to other_unknown
    for tag_query in OTHER_UNKNOWN_TAGS:
        download_class("other_unknown", tag_query, new_needed=5, new_train_count=4)