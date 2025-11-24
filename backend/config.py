# backend/config.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("MUSIQ_DATA_DIR", BASE_DIR / "data"))
IMAGE_DIR = DATA_DIR / "image"

# Garante que as pastas existem
for d in (DATA_DIR, IMAGE_DIR):
    d.mkdir(parents=True, exist_ok=True)
