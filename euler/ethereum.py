import requests
import csv
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")

START_TIME ="1639249208"
URL = f'https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/95nyAWFFaiz6gykko3HtBCyhRuP5vZzuKYsZiLxHxLhr'

FIRST_PART_QUERY = """
{
  financialsDailySnapshots(
    first: 1000
    orderBy: timestamp
    orderDirection: asc
    where: {timestamp_gt: \""""

SECOND_PART_QUERY = """\"}
  ) {
    totalValueLockedUSD
    totalDepositBalanceUSD
    totalBorrowBalanceUSD
    timestamp
  }
}
"""

keys = None
current_time = START_TIME
snapshots = []

while True:
    query = FIRST_PART_QUERY + str(current_time) + SECOND_PART_QUERY
    response = requests.post(URL,
                             '',
                             json={'query': query})
    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["financialsDailySnapshots"]
    except (AttributeError, KeyError) as error:
        print("Error at timestamp", current_time)
        print(error)
        continue
    if len(data) == 0:
        break
    if keys is None:
        keys = data[0].keys()
    print(len(data), "rows found at timestamp", current_time)
    snapshots += data
    current_time = int(data[-1]["timestamp"])

with open('euler_ethereum.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(snapshots)
