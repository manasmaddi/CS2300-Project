import os
import hashlib
from datetime import datetime

def generate_cache_key(data_list):
    """
    Generate a simple hash from list of dates or values to check if anything changed.
    """
    raw_string = "|".join(str(item) for item in data_list)
    return hashlib.md5(raw_string.encode()).hexdigest()

def is_cache_valid(cache_file, current_key):
    if not os.path.exists(cache_file):
        return False

    with open(cache_file, "r") as f:
        saved_key = f.read().strip()
    return saved_key == current_key

def update_cache_file(cache_file, key):
    with open(cache_file, "w") as f:
        f.write(key)
