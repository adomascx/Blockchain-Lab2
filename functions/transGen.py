import json
import random
from functions.hash import HashFunction

MAX_TRANSACTIONS = 1000


def transactionGeneration():
    """
    Generate a list of random transactions based on initial user balances.
    This function creates a UTXO (Unspent Transaction Output) set from user balances
    and generates up to 10,000 random transactions by selecting random inputs and 
    receivers, splitting amounts, and creating appropriate outputs with change.
    Returns:
        list: A list of transaction dictionaries, where each transaction contains:
            - transaction_id (str): Hash of the transaction
            - inputs (list): List of input UTXO IDs being spent
            - outputs (list): List of output UTXOs, including:
                - ID (str): Hash identifier for the UTXO
                - owner (str): Public key of the UTXO owner
                - amount (int): Amount in the UTXO
    Notes:
        - Reads user data from "json/users_start.json"
        - Each transaction transfers 1-15% of the input amount to a random receiver
        - Change is returned to the original owner
        - Uses HashFunction for generating unique IDs
        - Stops early if UTXO set becomes empty
    """
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
    for _ in range(MAX_TRANSACTIONS):
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