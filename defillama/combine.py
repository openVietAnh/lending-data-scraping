import os
import csv
from datetime import datetime
from collections import defaultdict

BORROW_INCLUDED = True

def read_file_data(file_path):
    """
    Returns a dictionary with date as key and (supply, borrow) tuple as value.
    """
    data = {}
    with open(file_path, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
                supply = float(row["Total Supply"])
                borrow = float(row["Total Borrow"])
                data[date] = (supply, borrow)
            except Exception as e:
                print(f"Skipping row in {file_path}: {row} (Error: {e})")
    return data

def combine_ratios(folder_path, output_file):
    all_dates = set()
    file_data = {}

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            name = os.path.splitext(file)[0]
            data = read_file_data(file_path)
            file_data[name] = data
            all_dates.update(data.keys())

    sorted_dates = sorted(all_dates)

    aave_totals = defaultdict(lambda: [0.0, 0.0])
    compound_totals = defaultdict(lambda: [0.0, 0.0])

    for name, data in file_data.items():
        for date in sorted_dates:
            supply, borrow = data.get(date, (0.0, 0.0))
            if name.startswith("AAVE"):
                aave_totals[date][0] += supply
                aave_totals[date][1] += borrow
            elif name.startswith("Compound"):
                compound_totals[date][0] += supply
                compound_totals[date][1] += borrow

    with open(output_file, mode='w', newline='') as f:
        fieldnames = ["Date"] + sorted(file_data.keys()) + ["AAVE combined", "Compound combined"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for date in sorted_dates:
            row = {"Date": date.strftime("%d/%m/%Y")}

            for name in file_data:
                supply, borrow = file_data[name].get(date, (0.0, 0.0))
                if supply != 0:
                    ratio = borrow / (borrow + supply) if BORROW_INCLUDED else borrow / supply
                    row[name] = f"{ratio:.6f}"
                else:
                    row[name] = ""

            aave_supply, aave_borrow = aave_totals[date]
            if aave_supply != 0:
                aave_ratio = aave_borrow / (aave_borrow + aave_supply) if BORROW_INCLUDED else aave_borrow / aave_supply
                row["AAVE combined"] = f"{aave_ratio:.6f}"
            else:
                row["AAVE combined"] = ""

            compound_supply, compound_borrow = compound_totals[date]
            if compound_supply != 0:
                compound_ratio = compound_borrow / (compound_borrow + compound_supply) if BORROW_INCLUDED else compound_borrow / compound_supply
                row["Compound combined"] = f"{compound_ratio:.6f}"
            else:
                row["Compound combined"] = ""

            writer.writerow(row)

    print(f"Combined CSV written to: {output_file}")

if __name__ == "__main__":
    combine_ratios(folder_path="totals", output_file="combined_borrows_included_AAVE_Compound.csv")
