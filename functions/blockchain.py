from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count

from functions.block import Block
from functions.hash import HashFunction


def _mine_candidate_worker(args):
    """Worker function for parallel mining of a single candidate block."""
    candidate, max_attempts, difficulty, candidate_idx = args
    prefix = "0" * difficulty
    
    for _ in range(max_attempts):
        computed_hash = candidate.calculate_hash()
        if computed_hash.startswith(prefix):
            return (candidate_idx, candidate, computed_hash, True)
        candidate.nonce += 1
    
    return (candidate_idx, None, None, False)


@dataclass
class UserAccount:
    name: str
    public_key: str
    balance: int

    def to_dict(self):
        return {"name": self.name, "public_key": self.public_key, "balance": self.balance}


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: int
    transaction_id: str = ""
    raw_payload: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.transaction_id:
            payload = f"{self.sender}|{self.receiver}|{self.amount}"
            self.transaction_id = HashFunction(payload)

    @classmethod
    def from_dict(cls, payload, utxo_map=None):
        # Handle UTXO-based transactions
        if "inputs" in payload and "outputs" in payload:
            outputs = payload.get("outputs", []) or []
            receiver = str(outputs[0].get("owner", "")) if outputs else ""
            
            if len(outputs) >= 2:
                sender = str(outputs[1].get("owner", ""))
            else:
                sender = ""
                inputs = payload.get("inputs", []) or []
                if inputs and utxo_map:
                    sender = utxo_map.get(str(inputs[0]), "")

            amount = int(outputs[0].get("amount", 0)) if outputs else 0
            tx_id = str(payload.get("transaction_id", ""))
            return cls(
                sender=sender, 
                receiver=receiver, 
                amount=amount,
                transaction_id=tx_id,
                raw_payload=payload
            )

        # Handle simple transactions
        sender = str(payload.get("sender", ""))
        receiver = str(payload.get("receiver", ""))
        amount = int(payload.get("amount", 0))
        tx_id = str(payload.get("transaction_id", ""))
        return cls(
            sender=sender, 
            receiver=receiver, 
            amount=amount,
            transaction_id=tx_id
        )

    def to_dict(self):
        if self.raw_payload:
            return self.raw_payload
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }


class Blockchain:
    """Basic blockchain implementation with parallel mining and UTXO support."""
    
    def __init__(self, users, transactions, difficulty=3, block_size=100):
        self.difficulty = difficulty
        self.block_size = block_size
        self.chain = []
        self.rejected = []
        self.users = {}
        
        # Create user accounts
        for user in users:
            pk = str(user["public_key"])
            self.users[pk] = UserAccount(
                name=str(user.get("name", "")),
                public_key=pk,
                balance=int(user.get("balance", 0))
            )

        # Build UTXO mapping for transaction parsing
        utxo_map = {}
        for tx in transactions:
            if not tx:
                continue
            outs = tx.get("outputs") or []
            for out in outs:
                u_id = out.get("ID")
                owner = out.get("owner")
                if u_id and owner:
                    utxo_map[str(u_id)] = str(owner)

        # Parse transactions
        self.pending_transactions = [Transaction.from_dict(tx, utxo_map) for tx in transactions if tx]
        random.shuffle(self.pending_transactions)

    def mine_pending_transactions(self):
        """Mine all pending transactions using parallel mining."""
        block_index = 1
        max_attempts = 1000
        
        while self.pending_transactions:
            print(f"\n=== Mining Block #{block_index} ===")
            print(f"Pending transactions: {len(self.pending_transactions)}")
            prev_hash = self.chain[-1].calculate_hash() if self.chain else "0" * 64
            
            # Create candidate blocks (without modifying pending_transactions)
            candidates = []
            for i in range(5):
                block_txs = self._select_transactions_for_candidate()
                if not block_txs:
                    break
                
                candidate = Block(
                    transactions=[tx.to_dict() for tx in block_txs],
                    prev_block_hash=prev_hash,
                    version="1.0.0",
                    difficulty_target=self.difficulty,
                    nonce=random.randint(0, 1000000)
                )
                candidates.append((candidate, block_txs))
            
            if not candidates:
                break
            
            print(f"Mining {len(candidates)} candidates in parallel...")
            
            # Parallel mining
            mined_block = None
            mined_txs = []
            winning_idx = -1
            attempts = max_attempts
            num_workers = min(len(candidates), cpu_count())
            
            while mined_block is None:
                worker_args = [
                    (candidate, attempts, self.difficulty, idx)
                    for idx, (candidate, txs) in enumerate(candidates)
                ]
                
                with Pool(processes=num_workers) as pool:
                    results = pool.map(_mine_candidate_worker, worker_args)
                
                for candidate_idx, candidate, result_hash, success in results:
                    if success:
                        print(f"Candidate #{candidate_idx+1} found valid hash!")
                        mined_block = candidate
                        mined_txs = candidates[candidate_idx][1]
                        winning_idx = candidate_idx
                        break
                
                if mined_block is None:
                    attempts += 500
            
            # Remove only the winning block's transactions from pending pool
            mined_tx_ids = {tx.transaction_id for tx in mined_txs}
            self.pending_transactions = [
                tx for tx in self.pending_transactions 
                if tx.transaction_id not in mined_tx_ids
            ]
            
            self._commit_block(mined_block, mined_txs)
            self.chain.append(mined_block)
            block_index += 1

    def _select_transactions_for_candidate(self):
        """Select valid transactions for a candidate block (non-destructive)."""
        if not self.pending_transactions:
            return []

        # Work with a shuffled copy to get variety in candidates
        available_txs = self.pending_transactions.copy()
        random.shuffle(available_txs)
        
        selection = []
        balances = {pk: acct.balance for pk, acct in self.users.items()}
        used_tx_ids = set()

        for tx in available_txs:
            # Skip if already used in this candidate
            if tx.transaction_id in used_tx_ids:
                continue
                
            if len(selection) >= self.block_size:
                break

            # Simple validation
            if tx.sender not in self.users or tx.receiver not in self.users:
                # Don't reject here, will be rejected when actually mined
                continue
            
            if tx.amount <= 0:
                continue
            
            if balances.get(tx.sender, 0) < tx.amount:
                continue

            selection.append(tx)
            used_tx_ids.add(tx.transaction_id)
            balances[tx.sender] -= tx.amount
            balances[tx.receiver] += tx.amount

        return selection

    def _commit_block(self, block, transactions):
        """Update user balances and reject invalid transactions after mining a block."""
        valid_count = 0
        for tx in transactions:
            # Validate transaction before committing
            if tx.sender not in self.users or tx.receiver not in self.users:
                self.rejected.append((tx, "unknown user"))
                continue
            
            if tx.amount <= 0:
                self.rejected.append((tx, "invalid amount"))
                continue
            
            if self.users[tx.sender].balance < tx.amount:
                self.rejected.append((tx, "insufficient balance"))
                continue
            
            # Apply valid transaction
            self.users[tx.sender].balance -= tx.amount
            self.users[tx.receiver].balance += tx.amount
            valid_count += 1
            
        print(f"Block mined with {valid_count} valid transactions ({len(transactions) - valid_count} rejected).")

    def to_dict(self):
        """Export blockchain to dictionary."""
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

    def export_users(self):
        """Export user accounts to list."""
        return [acct.to_dict() for acct in self.users.values()]

    def save_state(self, chain_path, users_path):
        """Save blockchain and users to JSON files."""
        with open(chain_path, "w", encoding="utf-8") as chain_file:
            json.dump(self.to_dict(), chain_file, indent=2)
        with open(users_path, "w", encoding="utf-8") as users_file:
            json.dump({"users": self.export_users()}, users_file, indent=2)