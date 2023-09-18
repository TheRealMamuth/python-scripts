# Account Data Summary

This script is designed to process JSON files containing account data. Based on this data, a summary is generated which can either be sent to Discord via a webhook or saved to a file.

## Installation

1. Ensure you have Python installed on your computer.
2. Clone the repository or download the contents to your machine.
3. Navigate to the directory containing the script.
4. Install the required libraries:

```bash
pip install -r requirements.txt
```

## How to use this scripts:

#### get-customer-balance.py
```bash
doctl balance get -t "YOUR_API_KEY" -o json | python3 "get-customer-balance.py" "your_account_name"
```

#### json-account-balance.py
```bash
python3 "json-account-summary.py" [--path PATH_TO_FILES] [--webhook "YOUR_WEBHOOK_URL"]
```

Options:

`--path`: Path to the directory containing the JSON files. Defaults to the current directory (./).

`--webhook`: The URL of the Discord webhook. If provided, the summary will be sent to Discord and save to file. If you do not provide a webhook, the results will be saved only in a file named summary.txt.