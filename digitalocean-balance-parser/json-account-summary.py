import json
import os
import requests
import argparse

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"

def get_usd_to_pln_rate():
    """
    Fetch the current exchange rate for USD to PLN.
    """
    response = requests.get(EXCHANGE_API_URL)
    if response.status_code == 200:
        data = response.json()
        return data["rates"]["PLN"]
    else:
        print(f"Failed to fetch exchange rate. Error: {response.status_code} - {response.text}")
        return None

def send_to_discord(webhook_url, message):
    """
    Sends a given message to the specified Discord webhook URL.
    """
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Summary successfully sent to Discord!")
    else:
        print(f"Error occurred: {response.status_code} - {response.text}")

def save_to_file(filename, message):
    """
    Saves a given message to the specified file.
    """
    with open(filename, 'w') as f:
        f.write(message)
    print(f"Summary saved to file {filename}.")

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Summarizes JSON files and sends results to Discord or saves to a file.")
    parser.add_argument("--webhook", help="Discord webhook URL.")
    parser.add_argument("--path", default="./", help="Path to the directory with JSON files. Default is the current directory.")
    
    args = parser.parse_args()
    
    # Initialize the totals
    total_month_to_date_balance = 0.0
    total_account_balance = 0.0
    total_month_to_date_usage = 0.0
    
    # List of JSON files in the specified directory
    files = [os.path.join(args.path, f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f)) and f.endswith('.json')]
    
    # Process each JSON file and update the totals
    for file_name in files:
        with open(file_name, 'r') as f:
            data = json.load(f)
            total_month_to_date_balance += float(data['month_to_date_balance'])
            total_account_balance += float(data['account_balance'])
            total_month_to_date_usage += float(data['month_to_date_usage'])

    usd_to_pln_rate = get_usd_to_pln_rate()
    if not usd_to_pln_rate:
        print("Failed to retrieve exchange rate. Exiting.")
        return

    total_month_to_date_balance_pln = total_month_to_date_balance * usd_to_pln_rate

    message = f"""
📊 ** ---===### SUMMARY ###===---**
💵 Month to Date Balance (USD): {total_month_to_date_balance:.2f} $
💰 Month to Date Balance (PLN): {total_month_to_date_balance_pln:.2f} zł
🔒 Account Balance (USD): {total_account_balance:.2f} $
📈 Month to Date Usage (USD): {total_month_to_date_usage:.2f} $
"""

    # If a webhook is provided, send the summary to Discord
    if args.webhook:
        send_to_discord(args.webhook, message)
    
    # Save the summary to a file
    save_to_file("summary.txt", message)

if __name__ == "__main__":
    main()
