# myapp/utils.py
import hashlib

def generate_purchase_hash(fan_id, plaque_id, album_id):
    raw_string = f"{fan_id}-{plaque_id}-{album_id}"
    return hashlib.sha256(raw_string.encode()).hexdigest()
