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


def write_json(path, key, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({key: data}, f, indent=2)


def read_json(path, key):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get(key, [])


def run_blockchain() -> None:
    users = read_json(USERS_START, "users")
    transactions = read_json(TRANSACTIONS, "transactions")
    if not users:
        print("\nNo user records found. Please generate users before starting the miner.\n")
        return
    if not transactions:
        print("\nNo transactions found. Please generate transactions before mining.\n")
        return

    print(f"\nLoaded {len(users)} users and {len(transactions)} pending transactions.")
    chain = Blockchain(users=users, transactions=transactions, difficulty=3, block_size=100)
    chain.mine_pending_transactions()
    chain.save_state(CHAIN_DUMP, USERS_END)
    if chain.rejected:
        print(f"{len(chain.rejected)} transactions were rejected during validation.")
    print(f"Blockchain now contains {len(chain.chain)} blocks. State saved to {CHAIN_DUMP}.")


def menu_choice() -> bytes:
    choice = msvcrt.getch()
    while choice not in [b"1", b"2", b"3", b"4"]:
        print("\nPlease enter 1, 2, 3, or 4.\n")
        choice = msvcrt.getch()
    return choice


while True:
    print("1. Generate Users\n2. Generate Transactions\n3. Mine Blockchain\n4. Exit")
    selected = menu_choice()

    if selected == b"1":
        users = userGeneration()
        write_json(USERS_START, "users", users)
        print("\nUser dataset generated.\n")
    elif selected == b"2":
        if not os.path.exists(USERS_START):
            print("\nPlease generate users before generating transactions.\n")
        else:
            transactions = transactionGeneration()
            write_json(TRANSACTIONS, "transactions", transactions)
            print("\nTransaction dataset generated.\n")
    elif selected == b"3":
        run_blockchain()
    elif selected == b"4":
        exit()