import pandas as pd
import requests
import time
import random
import os

# Configuration
API_URL = "http://localhost:8000/predict"
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "creditcard.csv")

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        Q-SHIELD: Live Data Stream Simulator              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        return

    print("Loading transaction database...")
    # Load dataset to simulate incoming data stream
    df = pd.read_csv(DATA_PATH)
    
    # Let's ensure we get a mix of legitimate and fraudulent transactions for the demo
    fraud_df = df[df['Class'] == 1]
    legit_df = df[df['Class'] == 0]
    
    print("Connecting to Q-Shield API at", API_URL)
    print("Streaming live transactions...\n")

    while True:
        try:
            # 10% chance to intentionally inject a known fraud case into the stream
            if random.random() < 0.10:
                row = fraud_df.sample(1).iloc[0]
                tx_type = " (Known Fraud Inject)"
            else:
                row = legit_df.sample(1).iloc[0]
                tx_type = ""
            
            # Format payload strictly to the API Schema
            payload = {
                "V1": row["V1"], "V2": row["V2"], "V3": row["V3"], "V4": row["V4"],
                "V5": row["V5"], "V6": row["V6"], "V7": row["V7"], "V8": row["V8"],
                "V9": row["V9"], "V10": row["V10"], "V11": row["V11"], "V12": row["V12"],
                "V13": row["V13"], "V14": row["V14"], "V15": row["V15"], "V16": row["V16"],
                "V17": row["V17"], "V18": row["V18"], "V19": row["V19"], "V20": row["V20"],
                "V21": row["V21"], "V22": row["V22"], "V23": row["V23"], "V24": row["V24"],
                "V25": row["V25"], "V26": row["V26"], "V27": row["V27"], "V28": row["V28"],
                "Amount": row["Amount"]
            }
            
            # Send to Q-Shield API
            response = requests.post(API_URL, json=payload, timeout=2)
            
            if response.status_code == 200:
                result = response.json()
                
                # Terminal colors for visibility
                color = "\033[91m" if result["prediction"] == 1 else "\033[92m"
                reset = "\033[0m"
                
                print(f"Tx Amount: ${row['Amount']:>7.2f} {tx_type:<20} | Q-Shield: {color}[{result['label']}] (Risk: {result['risk_percentage']}){reset}")
            else:
                print(f"API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the API running? (Run: `python api.py`)")
            break
        except Exception as e:
            print(f"Stream Error: {e}")
            
        # Wait a random interval between 0.5 to 2 seconds to simulate real-world arrival times
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    main()
