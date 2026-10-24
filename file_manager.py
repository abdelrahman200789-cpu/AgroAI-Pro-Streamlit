import csv
import json
import logging
import os

# إعداد ملف التوثيق Log
logging.basicConfig(
    filename='data/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_event(message):
    logging.info(message)

def load_crops_csv(filepath='data/crops.csv'):
    crops = []
    if os.path.exists(filepath):
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                crops.append(row)
    return crops

def load_rules_json(filepath='data/rules.json'):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_rules_json(rules, filepath='data/rules.json'):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(rules, file, indent=4)

def add_crop_csv(crop_dict, filepath='data/crops.csv'):
    file_exists = os.path.exists(filepath)
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["crop_name", "season", "soil_type", "recommended_temp"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(crop_dict)