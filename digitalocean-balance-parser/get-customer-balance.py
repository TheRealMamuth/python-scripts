import json
import sys

# JSON from stdin
data = json.load(sys.stdin)

# Account name from command line
account_name = sys.argv[1]
data["account_name"] = account_name

# Create filename
file_name = f"{account_name}.json"

# Zapisz dane do pliku
with open(file_name, 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Data are save to file: {file_name}.")
