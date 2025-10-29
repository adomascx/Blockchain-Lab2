import json
import random
from Functions.hash import HashFunction

def transactionGeneration():
    with open("json/users_start.json", "r", encoding="utf-8") as f:
        users = json.load(f).get("users", [])
    transactions = []
    for i in range(10000):
        sender = random.choice(users)
        receiver = random.choice(users)
        if len(users) > 1:
            while receiver is sender:
                receiver = random.choice(users)

        pct = random.uniform(0.01, 0.15)
        amount = max(1, int(float(sender.get("balance", 0)) * pct))

        transactions.append({
            "transaction_id": f"{HashFunction(str(sender['name'])+str(receiver['name'])+str(amount))}",
            "sender": sender["public_key"],
            "receiver": receiver["public_key"],
            "amount": amount,
        })
    return transactions