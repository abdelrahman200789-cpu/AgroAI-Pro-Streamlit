import csv
import json
import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_PATH = DATA_DIR / "app.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_event(message):
    logging.info(message)


def load_crops_csv(filepath=None):
    path = Path(filepath) if filepath else DATA_DIR / "crops.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_rules_json(filepath=None):
    path = Path(filepath) if filepath else DATA_DIR / "rules.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, list) else []


def save_rules_json(rules, filepath=None):
    path = Path(filepath) if filepath else DATA_DIR / "rules.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(rules, file, indent=4, ensure_ascii=False)


def add_crop_csv(crop_dict, filepath=None):
    path = Path(filepath) if filepath else DATA_DIR / "crops.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["crop_name", "season", "soil_type", "recommended_temp"]
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({key: crop_dict.get(key, "") for key in fields})
