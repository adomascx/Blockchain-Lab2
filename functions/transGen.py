import json
import random
from functions.hash import HashFunction


def transactionGeneration():
    with open("json/users_start.json", "r", encoding="utf-8") as f:
        users = json.load(f).get("users", [])
    UTXO = []
    for u in users:
        bal = int(float(u.get("balance", 0)))
        if bal > 0:
            UTXO.append({"ID": HashFunction(f"{u['public_key']}{bal}{random.random()}"), "owner": u["public_key"], "amount": bal})
    transactions = []
    for i in range(10000):
        if not UTXO:
            break
        inp = random.choice(UTXO)
        receiver = random.choice(users)
        if len(users) > 1:
            while receiver.get("public_key") == inp["owner"]:
                receiver = random.choice(users)

        recv_pk = receiver.get("public_key")
        amt = int(inp["amount"] * random.uniform(0.01, 0.15))
        amt = max(1, min(amt, inp["amount"]))
        if amt > inp["amount"]:
            continue
        UTXO = [u for u in UTXO if u["ID"] != inp["ID"]]
        out_recv = {"ID": HashFunction(f"{recv_pk}{amt}{random.random()}"), "owner": recv_pk, "amount": amt}
        UTXO.append(out_recv)
        outputs = [out_recv]
        change = inp["amount"] - amt
        out_change = {"ID": HashFunction(f"{inp['owner']}{change}{random.random()}"), "owner": inp["owner"], "amount": change}
        outputs.append(out_change)
        if change > 0:
            UTXO.append(out_change)
        tx_id = HashFunction(inp["ID"] + out_recv["ID"] + outputs[1]["ID"])
        transactions.append({"transaction_id": tx_id, "inputs": [inp["ID"]], "outputs": outputs})

    return transactions