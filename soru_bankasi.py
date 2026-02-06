import json
import os

SORU_DOSYA = "soru_bankasi.json"

def soru_bankasini_yukle():
    if not os.path.exists(SORU_DOSYA):
        with open(SORU_DOSYA, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(SORU_DOSYA, "r", encoding="utf-8") as f:
        return json.load(f)

def soru_bankasini_kaydet(data):
    with open(SORU_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

