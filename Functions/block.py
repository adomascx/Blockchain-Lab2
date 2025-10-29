from datetime import datetime
from typing import List, Dict, Any
from Functions.hash import HashFunction


class Block:
    """
    Block class for blockchain implementation.
    
    Contains header with metadata and body with transactions.
    """
    
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
        
        # Calculate merkle root (hash of all transactions)
        self.merkle_root = self._calculate_merkle_root()
    
    def _calculate_merkle_root(self) -> str:
        """
        Calculate the hash of all transactions using pha256().
        
        Returns:
            Merkle root hash as a string
        """
        # Combine all transactions into a single string
        transactions_string = str(self.transactions)
        
        # Use pha256 hash function from src.hash
        return HashFunction(transactions_string)
    
    def get_header(self) -> Dict[str, Any]:
        """
        Get the block header as a dictionary.
        
        Returns:
            Dictionary containing all header fields
        """
        return {
            "PrevBlockHash": self.prev_block_hash,
            "Timestamp": self.timestamp,
            "Version": self.version,
            "MerkleRoot": self.merkle_root,
            "Nonce": self.nonce,
            "DifficultyTarget": self.difficulty_target
        }
    
    def get_body(self) -> List[Dict[str, Any]]:
        """
        Get the block body (transactions).
        
        Returns:
            List of transactions
        """
        return self.transactions
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of the entire block.
        
        Returns:
            Block hash as a string
        """
        header_string = str(self.get_header())
        return HashFunction(header_string)
    
    def __repr__(self) -> str:
        """String representation of the block."""
        return f"Block(PrevHash={self.prev_block_hash[:16]}..., Transactions={len(self.transactions)}, Nonce={self.nonce})"
    
    def __str__(self) -> str:
        """Detailed string representation of the block."""
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
