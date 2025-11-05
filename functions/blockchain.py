from __future__ import annotations
import json
import random
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count
from functions.block import block
from functions.hash import HashFunction

def _mine_candidate_worker(args):
    """Worker for mining a single candidate block."""
    
    candidate, max_attempts, difficulty, candidate_index = args
    prefix = "0" * difficulty
    
    # Try to find a valid nonce within max_attempts
    for _ in range(max_attempts):
        computed_hash = candidate.calculate_hash()
        if computed_hash.startswith(prefix):
            return (candidate_index, candidate, computed_hash, True)
        candidate.nonce += 1

    # if max_attempts reached, return failure
    return (candidate_index, None, None, False)


@dataclass
class Transaction:
    """Represents a transaction with I/O and ID (UTXO model)."""
    inputs: list[str] = field(default_factory=list)
    outputs: list[dict] = field(default_factory=list)
    transaction_id: str = ""

    def __post_init__(self):
        # Generate transaction ID if not present in the JSON
        if not self.transaction_id:
            self.transaction_id = self._generate_id()

    @classmethod
    def from_dict(cls, payload):
        """Create Transaction instance from dict (for JSON)."""
        inputs = [str(value) for value in payload.get("inputs", [])]
        outputs = [
            {
                "ID": str(output.get("ID", "")),
                "owner": str(output.get("owner", "")),
                "amount": int(output.get("amount", 0)),
            }
            for output in payload.get("outputs", []) or []
        ]
        tx_id = str(payload.get("transaction_id", ""))
        return cls(inputs=inputs, outputs=outputs, transaction_id=tx_id)

    def to_dict(self):
        """Export Transaction to dict (for JSON)."""
        return {
            "transaction_id": self.transaction_id,
            "inputs": self.inputs,
            "outputs": self.outputs,
        }

    def _generate_id(self):
        """Helper - Generate transaction ID from hashed I/O."""
        payload_parts = ["".join(self.inputs)]
        payload_parts.append(
            "".join(str(out.get("ID", "")) for out in self.outputs)
        )
        return HashFunction("|".join(payload_parts))


class blockchain:
    """Basic blockchain implementation with parallel mining and UTXO."""
    
    def __init__(self, users, transactions, difficulty=3, block_size=100):
        self.difficulty = difficulty
        self.block_size = block_size
        self.chain = []
        self.rejected_count = 0
        self.utxo_index = {}
        # Parse all pending transactions
        self.pending_transactions = [Transaction.from_dict(tx) for tx in transactions if tx]

    def mine_pending_transactions(self, chain_path=None):
        """Mine all pending transactions using parallel mining."""
        block_index = len(self.chain) + 1
        max_attempts = 1000

        # Main mining loop
        while self.pending_transactions:
            print(f"\n=== Mining Block #{block_index} ===")
            print(f"Pending transactions: {len(self.pending_transactions)}")

            prev_hash = self.chain[-1].calculate_hash() if self.chain else "0" * 64

            # Build 5 candidate blocks
            candidates = self._build_candidates(prev_hash)
            if not candidates:
                break

            # Mine a block (from candidates)
            mined_block, mined_transactions = self._mine_candidates(candidates, max_attempts)
            if mined_block is None:
                break

            # Add the mined block to the blockchain
            self._finalize_mined_block(mined_block, mined_transactions, chain_path)
            block_index += 1

    def _build_candidates(self, prev_hash):
        """Build candidate blocks for mining."""
        candidates = []
        
        # Select 5 candidate blocks
        for _ in range(5):
            # Select 100 transactions
            block_transactions = self._select_transactions_for_candidate()
            if not block_transactions:
                break

            # Add header
            candidate = block(
                transactions=[tx.to_dict() for tx in block_transactions],
                prev_block_hash=prev_hash,
                version="0.2",
                difficulty_target=self.difficulty,
                nonce=random.randint(0, 1_000_000),
            )
            # Create candidate block
            candidates.append((candidate, block_transactions))

        return candidates
    
    def _select_transactions_for_candidate(self):
        """Select valid transactions for a candidate block."""
        if not self.pending_transactions:
            return []

        transaction_selection = []
        used_inputs = set()

        for tx in self.pending_transactions:
            # Is there space for more transactions
            if len(transaction_selection) >= self.block_size:
                break
            
            # Does the transaction have outputs
            if not tx.outputs:
                continue
            
            # Are all inputs used
            if any(inp in used_inputs for inp in tx.inputs):
                continue
            
            # If so, add transaction to selection
            transaction_selection.append(tx)
            used_inputs.update(tx.inputs)

        return transaction_selection

    def _mine_candidates(self, candidates, max_attempts):
        """Attempt to mine candidate blocks in parallel (with bounded attempts)."""
        mined_block = None
        mined_transactions = []
        attempts = max_attempts
        num_workers = min(len(candidates), cpu_count())

        while mined_block is None:
            
            # Prepare args for mining workers
            worker_args = [
                (candidate, attempts, self.difficulty, idx)
                for idx, (candidate, _) in enumerate(candidates)
            ]

            # Mine candidates using worker pool
            with Pool(processes=num_workers) as pool:
                results = pool.map(_mine_candidate_worker, worker_args)

            # Check workers for success
            for candidate_index, candidate, _result_hash, success in results:
                if success:
                    mined_block = candidate
                    mined_transactions = candidates[candidate_index][1]
                    print(f"Candidate #{candidate_index + 1} found valid hash! (max_attempts: {attempts})") # type: ignore
                    break

            # If none were successful, increase max attempts and try again
            if mined_block is None:
                attempts += 500

        return mined_block, mined_transactions

    def _finalize_mined_block(self, block, transactions, chain_path):
        """Finalize the mined block and update blockchain state."""
        mined_transaction_ids = {tx.transaction_id for tx in transactions}

        # Remove mined transactions from `pending_transactions`
        self.pending_transactions = [
            tx
            for tx in self.pending_transactions
            if tx.transaction_id not in mined_transaction_ids
        ]

        # Update UTXO and append block to chain
        self._commit_block(block, transactions)
        self.chain.append(block)
        if chain_path:
            self.save_state(chain_path)

    def _commit_block(self, block, transactions):
        """Update user balances and reject invalid transactions after mining a block."""
        valid_count = 0
        for tx in transactions:
            # Are all inputs unspent
            if not tx.outputs:
                self.rejected_count += 1
                continue

            valid_count += 1
            
            # Update UTXO index by removing spent inputs
            for utxo_id in tx.inputs:
                self.utxo_index.pop(utxo_id, None)
                
            # Add new outputs to the index
            for output in tx.outputs:
                out_id = output.get("ID")
                if out_id:
                    self.utxo_index[str(out_id)] = output

        rejected = len(transactions) - valid_count
        print(f"Block mined with {valid_count} valid transactions ({rejected} rejected).")

    def to_dict(self):
        """Export blockchain to dict (for JSON)."""
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
            "rejected_transactions": self.rejected_count,
        }

    def save_state(self, chain_path):
        """Save blockchain state to JSON"""
        with open(chain_path, "w", encoding="utf-8") as chain_file:
            json.dump(self.to_dict(), chain_file, indent=2)

# I am going to cry if I have to deal with this code for one more second