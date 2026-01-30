import csv
import os

def write_or_append_csv(data: dict, file_path: str):
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())

        # Write header only once
        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


