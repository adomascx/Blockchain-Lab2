import json
import msvcrt
import os

from Functions.blockchain import Blockchain
from Functions.transGen import transactionGeneration
from Functions.userGen import userGeneration

USERS_START = "json/users_start.json"
USERS_END = "json/users_end.json"
TRANSACTIONS = "json/transactions.json"
CHAIN_DUMP = "json/blockchain.json"


def write_json(path, key, data):
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
        print("No users found. Generate users first.")
        return
    if not transactions:
        print("No transactions found. Generate transactions first.")
        return

    print(f"Loaded {len(users)} users and {len(transactions)} pending transactions.")
    chain = Blockchain(users=users, transactions=transactions, difficulty=3, block_size=100)
    chain.mine_pending_transactions()
    chain.save_state(CHAIN_DUMP, USERS_END)
    if chain.rejected:
        print(f"{len(chain.rejected)} transactions were tossed for being invalid.")
    print(f"Blockchain contains {len(chain.chain)} blocks. State dumped to {CHAIN_DUMP}.")


def menu_choice() -> bytes:
    choice = msvcrt.getch()
    while choice not in [b"1", b"2", b"3", b"4"]:
        print("\nPick 1, 2, 3, or 4. That isn't complicated.\n")
        choice = msvcrt.getch()
    return choice


while True:
    print("1. Generate Users\n2. Generate Transactions\n3. Mine Blockchain\n4. Exit")
    selected = menu_choice()

    if selected == b"1":
        users = userGeneration()
        write_json(USERS_START, "users", users)
        print("\nUsers generated.\n")
    elif selected == b"2":
        transactions = transactionGeneration()
        write_json(TRANSACTIONS, "transactions", transactions)
        print("\nTransactions generated.\n")
    elif selected == b"3":
        run_blockchain()
    elif selected == b"4":
        exit()