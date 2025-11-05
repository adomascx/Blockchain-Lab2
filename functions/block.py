from datetime import datetime

from functions.hash import HashFunction


class Block:
    def __init__(self, transactions, prev_block_hash="0" * 64, version="0.2", difficulty_target=4, nonce=0):
        self.prev_block_hash = prev_block_hash
        self.timestamp = datetime.now().isoformat()
        self.version = version
        self.difficulty_target = difficulty_target
        self.nonce = nonce
        self.transactions = transactions if transactions else []
        self.merkle_root = self._calculate_merkle_root()

    def _calculate_merkle_root(self):
        if not self.transactions:
            return HashFunction("")

        # Build Merkle levels with a basic balanced approach
        level = []
        for tx in self.transactions:
            level.append(str(tx.get("transaction_id", "")))

        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])

            next_level = []
            index = 0
            while index < len(level):
                combined = level[index] + level[index + 1]
                next_level.append(HashFunction(combined))
                index += 2
            level = next_level

        return level[0]

    def get_header(self):
        return {
            "PrevBlockHash": self.prev_block_hash,
            "Timestamp": self.timestamp,
            "Version": self.version,
            "MerkleRoot": self.merkle_root,
            "Nonce": self.nonce,
            "DifficultyTarget": self.difficulty_target,
        }

    def get_body(self):
        return self.transactions

    def calculate_hash(self):
        header_parts = [
            self.prev_block_hash,
            self.timestamp,
            self.version,
            self.merkle_root,
            str(self.nonce),
            str(self.difficulty_target),
        ]
        return HashFunction("|".join(header_parts))
