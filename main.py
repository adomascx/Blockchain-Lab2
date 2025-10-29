import msvcrt
import json
from Functions.userGen import userGeneration
from Functions.transGen import transactionGeneration

def write_json(path, key, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({key: data}, f, indent=2)


while True:
    print ("1. Generate Users\n2. Generate Transactions\n3. Exit")
    choice = msvcrt.getch()
    while choice not in [b'1', b'2', b'3']:
        print("\nWRONG BITCH! Select 1, 2 or 3\n")
        choice = msvcrt.getch()
    if choice == b'1':
        users = userGeneration()
        write_json("json/users_start.json", "users", users)
        print("\nUsers generated successfully.\n")
    elif choice == b'2':
        transactions = transactionGeneration()
        write_json("json/transactions.json", "transactions", transactions)
        print("\nTransactions generated successfully.\n")
    elif choice == b'3':
        exit()