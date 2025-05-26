import csv
import os
from datetime import datetime, timedelta

def read_dates_from_csv(file_path):
    dates = []
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                date = datetime.strptime(row["Date"], "%d/%m/%Y")
                dates.append(date)
            except (ValueError, KeyError):
                print(f"[{os.path.basename(file_path)}] Skipping invalid or missing date: {row.get('Date', 'N/A')}")
    return sorted(dates)

def find_missing_dates(dates):
    missing = []
    for i in range(1, len(dates)):
        expected = dates[i-1] + timedelta(days=1)
        while expected < dates[i]:
            missing.append(expected)
            expected += timedelta(days=1)
    return missing

def check_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print(f"\nChecking file: {filename}")
            dates = read_dates_from_csv(file_path)

            if not dates:
                print("  No valid dates found.")
                continue

            missing_dates = find_missing_dates(dates)

            if missing_dates:
                print("  Missing dates:")
                for d in missing_dates:
                    print(f"    {d.strftime('%d/%m/%Y')}")
            else:
                print("  All dates are consecutive. No missing days.")

def main():
    folder_path = "./totals"
    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return
    check_folder(folder_path)

if __name__ == "__main__":
    main()
