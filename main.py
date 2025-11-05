# run with "py -3.12 main.py", older versions may print noisy warnings

import json
import msvcrt
import os

from functions.blockchain import Blockchain
from functions.transGen import transactionGeneration
from functions.userGen import userGeneration

USERS_START = "json/users_start.json"
USERS_END = "json/users_end.json"
TRANSACTIONS = "json/transactions.json"
CHAIN_DUMP = "json/blockchain.json"


def save_json(path, key, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({key: data}, handle, indent=2)


def load_json(path, key):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get(key, [])


def mine_blockchain():
    # Load users and check if exist
    users = load_json(USERS_START, "users")
    if not users:
        print("\nNo users found. Generate users before mining.\n")
        return

    # Load transactions and check if exist
    transactions = load_json(TRANSACTIONS, "transactions")
    if not transactions:
        print("\nNo transactions found. Generate transactions before mining.\n")
        return

    print(f"\nLoaded {len(users)} users and {len(transactions)} pending transactions.")
    
    # Init blockchain and start mining
    chain = Blockchain(users=users, transactions=transactions, difficulty=3, block_size=100)
    chain.mine_pending_transactions(chain_path=CHAIN_DUMP, users_path=USERS_END)
    if chain.rejected:
        print(f"{len(chain.rejected)} transactions were rejected during validation.")
    print(f"Blockchain now contains {len(chain.chain)} blocks. Saved to {CHAIN_DUMP}.")


def menu_choice():
    while True:
        choice = msvcrt.getch()
        if choice in (b"1", b"2", b"3", b"4"):
            return choice.decode("ascii")
        print("\nPlease press 1, 2, 3, or 4.\n")


def main():
    while True:
        print("1. Generate Users\n2. Generate Transactions\n3. Mine Blockchain\n4. Exit")
        choice = menu_choice()

        if choice == "1":
            users = userGeneration()
            save_json(USERS_START, "users", users)
            print("\nUsers generated.\n")
        elif choice == "2":
            if not os.path.exists(USERS_START):
                print("\nPlease generate users before generating transactions.\n")
            else:
                transactions = transactionGeneration()
                save_json(TRANSACTIONS, "transactions", transactions)
                print("\nTransactions generated.\n")
        elif choice == "3":
            mine_blockchain()
        elif choice == "4":
            break


if __name__ == "__main__":
    main()