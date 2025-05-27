import os
import csv
from datetime import datetime
from collections import defaultdict

BORROW_INCLUDED = True

def read_file_ratios(file_path):
    ratios = {}
    with open(file_path, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
                supply = float(row["Total Supply"])
                borrow = float(row["Total Borrow"])
                if supply != 0:
                    ratio = borrow / (borrow + supply) if BORROW_INCLUDED else borrow / supply
                    ratios[date] = ratio
            except Exception as e:
                print(f"Skipping row in {file_path}: {row} (Error: {e})")
    return ratios

def combine_ratios(folder_path, output_file):
    all_dates = set()
    file_ratios = {}

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            name = os.path.splitext(file)[0]
            ratios = read_file_ratios(file_path)
            file_ratios[name] = ratios
            all_dates.update(ratios.keys())

    sorted_dates = sorted(all_dates)

    with open(output_file, mode='w', newline='') as f:
        fieldnames = ["Date"] + sorted(file_ratios.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for date in sorted_dates:
            row = {"Date": date.strftime("%d/%m/%Y")}
            for name in file_ratios:
                value = file_ratios[name].get(date)
                row[name] = f"{value:.6f}" if value is not None else ""
            writer.writerow(row)

    print(f"Combined CSV written to: {output_file}")

if __name__ == "__main__":
    combine_ratios(folder_path="totals", output_file="combined_borrows_included.csv")