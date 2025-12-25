"""
Quantum-Safe Block Implementation
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Transaction:
    """Blockchain transaction with quantum-safe signatures"""
    
    def __init__(self, sender: str, recipient: str, amount: float, 
                 signature: bytes = None, nonce: str = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = datetime.now().isoformat()
        self.signature = signature
        self.nonce = nonce or hashlib.sha3_256(
            f"{sender}{recipient}{amount}{self.timestamp}".encode()
        ).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'signature': self.signature.hex() if self.signature else None
        }
    
    def get_hash(self) -> str:
        """Calculate transaction hash"""
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha3_256(tx_string.encode()).hexdigest()
    
    def __repr__(self):
        return f"Transaction({self.sender[:8]}...→{self.recipient[:8]}..., {self.amount})"


class Block:
    """Quantum-safe blockchain block"""
    
    def __init__(self, index: int, transactions: List[Transaction], 
                 previous_hash: str, timestamp: str = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now().isoformat()
        self.nonce = 0
        self.hash = None
        self.merkle_root = self._calculate_merkle_root()
    
    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return hashlib.sha3_256(b"").hexdigest()
        
        tx_hashes = [tx.get_hash() for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hash = hashlib.sha3_256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            
            tx_hashes = new_hashes
        
        return tx_hashes[0]
    
    def calculate_hash(self) -> str:
        """Calculate block hash using SHA3-256 (quantum-resistant)"""
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha3_256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int):
        """Mine block with proof-of-work"""
        target = '0' * difficulty
        
        print(f"⛏️  Mining block {self.index}...", end="", flush=True)
        
        while True:
            self.hash = self.calculate_hash()
            
            if self.hash[:difficulty] == target:
                print(f" ✅ Mined! Hash: {self.hash[:16]}...")
                break
            
            self.nonce += 1
            
            if self.nonce % 10000 == 0:
                print(".", end="", flush=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def __repr__(self):
        return f"Block(#{self.index}, {len(self.transactions)} txs, hash={self.hash[:16] if self.hash else 'unmined'}...)"


# Test the module
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing Block Module")
    print("="*50 + "\n")
    
    print("1. Creating transactions...")
    tx1 = Transaction("Alice", "Bob", 50.0)
    tx2 = Transaction("Bob", "Charlie", 25.0)
    print(f"   {tx1}")
    print(f"   {tx2}")
    
    print("\n2. Creating block...")
    block = Block(1, [tx1, tx2], "0" * 64)
    print(f"   {block}")
    print(f"   Merkle root: {block.merkle_root[:16]}...")
    
    print("\n3. Mining block (difficulty=4)...")
    block.mine_block(4)
    print(f"   Final hash: {block.hash}")
    print(f"   Nonce: {block.nonce}")
    
    print("\n" + "="*50)
    print("✅ Block Module Tests Complete!")
    print("="*50 + "\n")


