import json
import os
import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

data_path = 'data.json'
if not os.path.exists(data_path):
    log("data.json not found")
    exit()

log("Loading data.json...")
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

exclude_combos = [
    ('디지털과 직업 생활', '공화'),
    ('디지털과 직업 생활', '기계'),
]

initial_count = len(data)
cleaned_data = []
removed_count = 0

log(f"Starting cleanup of {initial_count} items...")

for item in data:
    subj = item.get('subject')
    code_raw = item.get('code', '')
    code = code_raw.strip('[]')
    
    is_invalid = any(
        subj == target_subj and code.startswith(prefix)
        for target_subj, prefix in exclude_combos
    )
    
    if is_invalid:
        log(f"Removing: {subj} - {code_raw}")
        removed_count += 1
    else:
        cleaned_data.append(item)

if removed_count > 0:
    log("Saving cleaned data...")
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
else:
    log("No items found to remove.")

log(f"Initial: {initial_count}, Cleaned: {len(cleaned_data)}, Removed: {removed_count}")
