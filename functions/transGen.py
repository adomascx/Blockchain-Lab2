import json
import random
from functions.hash import HashFunction

TRANSACTIONS_COUNT = 1000

def transactionGeneration():
    def _new_utxo(owner: str, amount: int) -> dict:
        return {
            "ID": HashFunction(f"{owner}{amount}{random.random()}"),
            "owner": owner,
            "amount": amount
        }

    with open("json/users_start.json", "r", encoding="utf-8") as f:
        users = json.load(f).get("users", [])

    utxo_pool = []
    for user in users:
        balance = int(float(user.get("balance", 0)))
        if balance > 0:
            utxo_pool.append(_new_utxo(user["public_key"], balance))

    transactions = []
    for _ in range(TRANSACTIONS_COUNT):
        if not utxo_pool:
            break

        spent_utxo = random.choice(utxo_pool)
        utxo_pool.remove(spent_utxo)

        receiver = random.choice(users)
        if len(users) > 1:
            while receiver.get("public_key") == spent_utxo["owner"]:
                receiver = random.choice(users)

        transfer_amount = max(1, int(spent_utxo["amount"] * random.uniform(0.01, 0.15)))
        transfer_amount = min(transfer_amount, spent_utxo["amount"])

        receiver_utxo = _new_utxo(receiver.get("public_key"), transfer_amount)
        utxo_pool.append(receiver_utxo)

        outputs = [receiver_utxo]
        change_amount = spent_utxo["amount"] - transfer_amount
        if change_amount > 0:
            change_utxo = _new_utxo(spent_utxo["owner"], change_amount)
            utxo_pool.append(change_utxo)
            outputs.append(change_utxo)

        output_ids = "".join(out["ID"] for out in outputs)
        tx_id = HashFunction(spent_utxo["ID"] + output_ids)

        transactions.append({
            "transaction_id": tx_id,
            "inputs": [spent_utxo["ID"]],
            "outputs": outputs
        })

    return transactions