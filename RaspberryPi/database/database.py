import pymongo
from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME, COLLECTION_ENCODING
from pymongo import MongoClient

import os
import json

ENCODINGS_PATH = "./encodings"  # Make sure this matches your actual path

def get_faces_from_local(division):
    """Returns list of (name, encoding) tuples from local JSON file for a specific division."""
    encoding_file = os.path.join(ENCODINGS_PATH, f"{division}.json")

    if not os.path.exists(encoding_file):
        print(f"❌ Encoding file for Division '{division}' not found.")
        return []

    with open(encoding_file, "r") as f:
        data = json.load(f)

    all_faces = []
    for name, encodings in data.items():
        for enc in encodings:
            all_faces.append((name, enc))

    return all_faces


from pymongo import MongoClient
def get_collection(division):
    client = MongoClient(MONGO_URI)
    db = client['wallseye']
    return db['Attendance']
