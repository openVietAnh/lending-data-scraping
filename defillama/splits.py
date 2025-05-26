import csv
import os

FILES = [
    "aries-markets",
    "avalon-usda",
    "benqi-lending",
    "dolomite",
    "echo-lending",
    "lista-lending",
    "navi-lending",
    "silo-v2",
    "suilend",
    "yei-finance"
]

def split_csv_by_chain(input_csv):
    name = input_csv.split('.')[0]
    with open(input_csv, mode='r', newline='') as file:
        reader = list(csv.reader(file))

    header = reader[0]
    second_row = reader[2]
    third_row = reader[3]

    date_idx = None
    timestamp_idx = None
    for idx, col_name in enumerate(header):
        name = col_name.strip().lower()
        if name == "date":
            date_idx = idx
        elif name == "timestamp":
            timestamp_idx = idx

    if date_idx is None or timestamp_idx is None:
        raise ValueError("Could not find 'Date' and 'Timestamp' columns.")

    chain_columns = {}  # chain_name -> { 'tvl': col_index, 'borrowed': col_index }
    total_case = {}     # Special case for total/borrowed

    for idx in range(len(header)):
        if idx == date_idx or idx == timestamp_idx:
            continue

        if idx < len(third_row) and third_row[idx] == "TVL":
            chain_info = second_row[idx].strip()
            col_name = header[idx].strip().lower()                
            if chain_info.endswith("-borrowed"):
                chain_name = chain_info[:-9]
                chain_columns.setdefault(chain_name, {})['borrowed'] = idx
            else:
                if chain_info == "Total":
                    total_case['tvl'] = idx
                elif chain_info == "borrowed":
                    total_case['borrowed'] = idx
                else:
                    chain_name = chain_info
                    chain_columns.setdefault(chain_name, {})['tvl'] = idx

    os.makedirs(name + "_output", exist_ok=True)

    for chain, cols in chain_columns.items():
        output_file = os.path.join(name + "_output", f"{chain}.csv")
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            headers = ["Date", "Timestamp", "TVL", "Total Supply"]
            if 'borrowed' in cols:
                headers.append("Total Borrow")
            writer.writerow(headers)

            for row in reader[5:]:  # skip first 4 rows after header
                new_row = [
                    row[date_idx],     # Date
                    row[timestamp_idx], # Timestamp
                    row[cols['tvl']],   # TVL
                    row[cols['tvl']],   # Total Supply (clone TVL)
                ]
                if 'borrowed' in cols:
                    new_row.append(row[cols['borrowed']])
                writer.writerow(new_row)

    if 'tvl' in total_case:
        output_file = os.path.join(name + "_output", "total.csv")
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            headers = ["Date", "Timestamp", "TVL", "Total Supply"]
            if 'borrowed' in total_case:
                headers.append("Total Borrow")
            writer.writerow(headers)

            for row in reader[5:]:
                new_row = [
                    row[date_idx],
                    row[timestamp_idx],
                    row[total_case['tvl']],
                    row[total_case['tvl']],
                ]
                if 'borrowed' in total_case:
                    new_row.append(row[total_case['borrowed']])
                writer.writerow(new_row)

if __name__ == "__main__":
    for item in FILES:
        split_csv_by_chain(item + ".csv")
