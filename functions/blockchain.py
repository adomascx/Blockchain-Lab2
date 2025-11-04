from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from functions.block import Block
from functions.hash import HashFunction


@dataclass
class UserAccount:
    name: str
    public_key: str
    balance: int

    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "public_key": self.public_key, "balance": self.balance}


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: int
    transaction_id: str = field(init=False)

    def __post_init__(self) -> None:
        payload = f"{self.sender}|{self.receiver}|{self.amount}"
        self.transaction_id = HashFunction(payload)

    @classmethod
    def from_dict(cls, payload: Dict[str, object], utxo_map: Dict[str, str] | None = None) -> "Transaction":
        if "inputs" in payload and "outputs" in payload:
            outputs = payload.get("outputs", []) or []
            receiver = str(outputs[0].get("owner", "")).strip() if len(outputs) >= 1 else ""
            if len(outputs) >= 2:
                sender = str(outputs[1].get("owner", "")).strip()
            else:
                sender = ""
                inputs = payload.get("inputs", []) or []
                if inputs and utxo_map:
                    sender = str(utxo_map.get(str(inputs[0]), "")).strip()

            amount = int(outputs[0].get("amount", 0)) if len(outputs) >= 1 else int(payload.get("amount", 0))
            instance = cls(sender=sender, receiver=receiver, amount=amount)
            instance.raw_payload = payload
            claimed = str(payload.get("transaction_id", "")).strip()
            if claimed:
                instance.transaction_id = claimed
            return instance

        sender = str(payload.get("sender", "")).strip()
        receiver = str(payload.get("receiver", "")).strip()
        amount = int(payload.get("amount", 0))
        instance = cls(sender=sender, receiver=receiver, amount=amount)
        claimed = str(payload.get("transaction_id", "")).strip()
        if claimed and claimed != instance.transaction_id:
            instance.transaction_id = claimed
        return instance

    def to_dict(self) -> Dict[str, object]:
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }


class Blockchain:
    def __init__(
        self,
        users: List[Dict[str, object]],
        transactions: List[Dict[str, object]],
        difficulty: int = 3,
        block_size: int = 100,
    ) -> None:
        if difficulty < 1:
            raise ValueError("Difficulty must be at least 1")
        if block_size < 1:
            raise ValueError("Block size must be at least 1")

        self.difficulty = difficulty
        self.block_size = block_size
        self.chain: List[Block] = []
        self.rejected: List[Tuple[Transaction, str]] = []
        self.users: Dict[str, UserAccount] = {
            str(user["public_key"]): UserAccount(
                name=str(user.get("name", "")),
                public_key=str(user.get("public_key", "")),
                balance=int(user.get("balance", 0)),
            )
            for user in users
        }

        
        utxo_map: Dict[str, str] = {}
        for tx in transactions:
            if not tx:
                continue
            outs = tx.get("outputs") or []
            for out in outs:
                u_id = out.get("UTXO_id")
                owner = out.get("owner")
                if u_id and owner:
                    utxo_map[str(u_id)] = str(owner)

        pending: List[Transaction] = [Transaction.from_dict(tx, utxo_map=utxo_map) for tx in transactions if tx]
        self.pending_transactions = pending

        random.shuffle(self.pending_transactions)

    def mine_pending_transactions(self) -> None:
        block_index = 1
        while self.pending_transactions:
            block_transactions = self._select_transactions_for_block()
            if not block_transactions:
                break

            prev_hash = self.chain[-1].calculate_hash() if self.chain else "0" * 64
            block = Block(
                transactions=[tx.to_dict() for tx in block_transactions],
                prev_block_hash=prev_hash,
                version="1.0.0",
                difficulty_target=self.difficulty,
            )

            print(f"\nPreparing block #{block_index} with {len(block_transactions)} transactions...")
            mined_hash = self._proof_of_work(block)
            print(f"Block #{block_index} mined with hash {mined_hash[:16]}... after nonce {block.nonce}")

            self._commit_block(block, block_transactions)
            self.chain.append(block)
            block_index += 1

        if self.pending_transactions:
            print("Mining stopped. Pending transactions remain that require validation.")

    def _select_transactions_for_block(self) -> List[Transaction]:
        if not self.pending_transactions:
            return []

        random.shuffle(self.pending_transactions)
        selection: List[Transaction] = []
        remaining: List[Transaction] = []
        shadow_balances = {pk: acct.balance for pk, acct in self.users.items()}

        for tx in self.pending_transactions:
            if len(selection) >= self.block_size:
                remaining.append(tx)
                continue

            valid, reason = self._validate_transaction(tx, shadow_balances)
            if valid:
                selection.append(tx)
                shadow_balances[tx.sender] -= tx.amount
                shadow_balances[tx.receiver] += tx.amount
            else:
                self.rejected.append((tx, reason))
                print(f"Rejected transaction {tx.transaction_id[:12]}... Reason: {reason}")

        self.pending_transactions = remaining
        return selection

    def _validate_transaction(self, tx: Transaction, balances: Dict[str, int]) -> Tuple[bool, str]:
        if tx.sender not in self.users:
            return False, "unknown sender"
        if tx.receiver not in self.users:
            return False, "unknown receiver"
        if tx.amount <= 0:
            return False, "non-positive amount"
        expected = HashFunction(f"{tx.sender}|{tx.receiver}|{tx.amount}")
        if tx.transaction_id != expected:
            
            sender_account = self.users[tx.sender]
            receiver_account = self.users[tx.receiver]
            legacy = HashFunction(f"{sender_account.name}{receiver_account.name}{tx.amount}")
            if tx.transaction_id == legacy:
                tx.transaction_id = expected
            else:
                
                raw = getattr(tx, "raw_payload", None)
                if raw and str(raw.get("transaction_id", "")).strip() == tx.transaction_id:
                    pass
                else:
                    return False, "forged transaction hash"
        if balances.get(tx.sender, 0) < tx.amount:
            return False, "insufficient balance"
        return True, ""

    def _proof_of_work(self, block: Block) -> str:
        prefix = "0" * self.difficulty
        attempt = 0
        while True:
            computed_hash = block.calculate_hash()
            if computed_hash.startswith(prefix):
                return computed_hash
            block.nonce += 1
            attempt += 1
            if attempt % 5000 == 0:
                print(f"Proof-of-work in progress; current nonce {block.nonce}")

    def _commit_block(self, block: Block, transactions: List[Transaction]) -> None:
        for tx in transactions:
            sender = self.users[tx.sender]
            receiver = self.users[tx.receiver]
            sender.balance -= tx.amount
            receiver.balance += tx.amount
        print(f"Committed block with {len(transactions)} confirmed transactions.")

    def to_dict(self) -> Dict[str, object]:
        return {
            "difficulty": self.difficulty,
            "block_size": self.block_size,
            "chain": [
                {
                    "header": block.get_header(),
                    "transactions": block.get_body(),
                    "hash": block.calculate_hash(),
                }
                for block in self.chain
            ],
            "rejected_transactions": [
                {"transaction": tx.to_dict(), "reason": reason}
                for tx, reason in self.rejected
            ],
        }

    def export_users(self) -> List[Dict[str, object]]:
        return [acct.to_dict() for acct in self.users.values()]

    def save_state(self, chain_path: str, users_path: str) -> None:
        with open(chain_path, "w", encoding="utf-8") as chain_file:
            json.dump(self.to_dict(), chain_file, indent=2)
        with open(users_path, "w", encoding="utf-8") as users_file:
            json.dump({"users": self.export_users()}, users_file, indent=2)