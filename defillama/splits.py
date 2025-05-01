import csv
import os

def split_csv_by_chain(input_csv):
    with open(input_csv, mode='r', newline='') as file:
        reader = list(csv.reader(file))

    header = reader[0]
    second_row = reader[2]
    third_row = reader[3]

    # --- Find the indexes of Date and Timestamp dynamically ---
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

    # --- Process the rest ---
    chain_columns = {}  # chain_name -> { 'tvl': col_index, 'borrowed': col_index }
    total_case = {}     # Special case for total/borrowed

    for idx in range(len(header)):
        if idx == date_idx or idx == timestamp_idx:
            continue  # skip Date and Timestamp columns

        if idx < len(third_row) and third_row[idx] == "TVL":
            chain_info = second_row[idx].strip()
            col_name = header[idx].strip().lower()

            if chain_info == "":  # empty chain name
                # Special case: match column names "total" and "borrowed"
                if col_name == "total":
                    total_case['tvl'] = idx
                elif col_name == "borrowed":
                    total_case['borrowed'] = idx
            else:
                if chain_info.endswith("-borrowed"):
                    chain_name = chain_info[:-9]  # remove "-borrowed"
                    chain_columns.setdefault(chain_name, {})['borrowed'] = idx
                else:
                    chain_name = chain_info
                    chain_columns.setdefault(chain_name, {})['tvl'] = idx

    os.makedirs("output", exist_ok=True)

    # Handle normal chains
    for chain, cols in chain_columns.items():
        output_file = os.path.join("output", f"{chain}.csv")
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

    # Handle special "total" case
    if 'tvl' in total_case:
        output_file = os.path.join("output", "total.csv")
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
    split_csv_by_chain("morpho-blue.csv")
