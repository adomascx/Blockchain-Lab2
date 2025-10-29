from datetime import datetime
from typing import List, Dict, Any
from functions.hash import HashFunction


class Block:
    """Represent a block composed of a header and an ordered transaction list."""
    
    def __init__(
        self,
        transactions: List[Dict[str, Any]],
        prev_block_hash: str = "0" * 64,
        version: str = "1.0.0",
        difficulty_target: int = 4,
        nonce: int = 0
    ):
        """
        Initialize a new block.
        
        Args:
            transactions: List of transaction dictionaries
            prev_block_hash: Hash of the previous block in the chain
            version: Data structure version
            difficulty_target: Difficulty level for Proof-of-Work
            nonce: Random number used in Proof-of-Work process
        """
        # Header components
        self.prev_block_hash = prev_block_hash
        self.timestamp = datetime.now().isoformat()
        self.version = version
        self.difficulty_target = difficulty_target
        self.nonce = nonce
        
        # Body
        self.transactions = transactions
        
        # Calculate the Merkle-style root by hashing all transaction identifiers
        self.merkle_root = self._calculate_merkle_root()
    
    def _calculate_merkle_root(self) -> str:
        """Calculate the hash of all transactions using the project HashFunction."""
        transaction_ids = [
            str(tx.get("transaction_id", "")) for tx in self.transactions
        ]
        combined = "|".join(transaction_ids)
        return HashFunction(combined)
    
    def get_header(self) -> Dict[str, Any]:
        """Return the block header as a dictionary."""
        return {
            "PrevBlockHash": self.prev_block_hash,
            "Timestamp": self.timestamp,
            "Version": self.version,
            "MerkleRoot": self.merkle_root,
            "Nonce": self.nonce,
            "DifficultyTarget": self.difficulty_target
        }
    
    def get_body(self) -> List[Dict[str, Any]]:
        """Return the transactions stored in the block body."""
        return self.transactions
    
    def calculate_hash(self) -> str:
        """Return the hash of the serialized block header."""
        header_string = str(self.get_header())
        return HashFunction(header_string)
    
    def __repr__(self) -> str:
        """Provide a concise representation for debugging."""
        return f"Block(PrevHash={self.prev_block_hash[:16]}..., Transactions={len(self.transactions)}, Nonce={self.nonce})"
    
    def __str__(self) -> str:
        """Provide a human-readable description of the block contents."""
        return f"""
Block Details:
--------------
Header:
  Previous Block Hash: {self.prev_block_hash}
  Timestamp: {self.timestamp}
  Version: {self.version}
  Merkle Root: {self.merkle_root}
  Nonce: {self.nonce}
  Difficulty Target: {self.difficulty_target}

Body:
  Transactions: {len(self.transactions)}
  Block Hash: {self.calculate_hash()}
"""
