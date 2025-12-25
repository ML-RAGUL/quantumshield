"""
Quantum-Safe Blockchain Implementation
"""

import json
from datetime import datetime
from typing import List, Optional
from blockchain.block import Block, Transaction
from blockchain.pqc_crypto import PQCKeyPair, PQCSignature


class Blockchain:
    """Main blockchain class with quantum-safe features"""
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.mining_reward = 10.0
        self.wallets = {}  # address -> keypair
        
        # Create genesis block
        print("🔷 Creating genesis block...")
        self._create_genesis_block()
        print(f"✅ Blockchain initialized with difficulty {difficulty}")
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_tx = Transaction("System", "Genesis", 0, nonce="genesis")
        genesis_block = Block(0, [genesis_tx], "0" * 64, 
                             timestamp="2025-01-01T00:00:00")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def create_wallet(self, name: str) -> str:
        """Create a new wallet with PQC keypair"""
        keypair = PQCKeyPair()
        address = keypair.get_address()
        self.wallets[address] = {
            'name': name,
            'keypair': keypair,
            'balance': 0
        }
        print(f"💼 Wallet created for {name}")
        print(f"   Address: {address}")
        return address
    
    def add_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        """Add a transaction to pending transactions"""
        
        # Validate sender has enough balance
        if sender != "System":
            sender_balance = self.get_balance(sender)
            if sender_balance < amount:
                print(f"❌ Insufficient balance. Has: {sender_balance}, Needs: {amount}")
                return False
        
        # Create and sign transaction
        transaction = Transaction(sender, recipient, amount)
        
        if sender in self.wallets:
            keypair = self.wallets[sender]['keypair']
            message = f"{sender}{recipient}{amount}"
            signature = PQCSignature.sign(message, keypair)
            transaction.signature = signature
        
        self.pending_transactions.append(transaction)
        print(f"📝 Transaction added: {sender[:8]}... → {recipient[:8]}... ({amount})")
        return True
    
    def mine_pending_transactions(self, miner_address: str):
        """Mine all pending transactions and reward the miner"""
        
        if not self.pending_transactions:
            print("⚠️  No transactions to mine")
            return None
        
        print(f"\n⛏️  Mining {len(self.pending_transactions)} transaction(s)...")
        
        # Create block with pending transactions
        block = Block(
            len(self.chain),
            self.pending_transactions,
            self.get_latest_block().hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(block)
        print(f"✅ Block #{block.index} added to chain!")
        
        # Reset pending transactions and reward miner
        self.pending_transactions = [
            Transaction("System", miner_address, self.mining_reward, nonce="reward")
        ]
        print(f"💰 Mining reward ({self.mining_reward}) sent to miner")
        
        return block
    
    def get_balance(self, address: str) -> float:
        """Calculate balance for an address"""
        balance = 0
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        
        # Include pending transactions
        for tx in self.pending_transactions:
            if tx.recipient == address:
                balance += tx.amount
            if tx.sender == address:
                balance -= tx.amount
        
        return balance
    
    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Block #{i} hash is invalid")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block #{i} previous hash doesn't match")
                return False
            
            # Check proof of work
            if not current_block.hash.startswith('0' * self.difficulty):
                print(f"❌ Block #{i} doesn't meet difficulty requirement")
                return False
        
        return True
    
    def get_chain_info(self) -> dict:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        return {
            'blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'latest_hash': self.get_latest_block().hash,
            'is_valid': self.is_chain_valid()
        }
    
    def print_chain(self):
        """Display the entire blockchain"""
        print("\n" + "="*60)
        print("🔗 BLOCKCHAIN")
        print("="*60)
        
        for block in self.chain:
            print(f"\n📦 Block #{block.index}")
            print(f"   Timestamp: {block.timestamp}")
            print(f"   Hash: {block.hash}")
            print(f"   Previous: {block.previous_hash[:16]}...")
            print(f"   Transactions: {len(block.transactions)}")
            for tx in block.transactions:
                print(f"      • {tx.sender[:8]}... → {tx.recipient[:8]}... : {tx.amount}")
        
        print("\n" + "="*60)
        print("📊 Chain Info:")
        info = self.get_chain_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        print("="*60 + "\n")


# Test the blockchain
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 QUANTUMSHIELD BLOCKCHAIN TEST")
    print("="*60 + "\n")
    
    # Create blockchain
    blockchain = Blockchain(difficulty=3)
    
    # Create wallets
    print("\n--- Creating Wallets ---")
    alice = blockchain.create_wallet("Alice")
    bob = blockchain.create_wallet("Bob")
    charlie = blockchain.create_wallet("Charlie")
    
    # Initial funding from System
    print("\n--- Initial Funding ---")
    blockchain.add_transaction("System", alice, 100)
    blockchain.mine_pending_transactions(alice)
    
    # Transactions
    print("\n--- User Transactions ---")
    blockchain.add_transaction(alice, bob, 30)
    blockchain.add_transaction(alice, charlie, 20)
    blockchain.mine_pending_transactions(bob)
    
    blockchain.add_transaction(bob, charlie, 15)
    blockchain.mine_pending_transactions(charlie)
    
    # Check balances
    print("\n--- Final Balances ---")
    print(f"💰 Alice: {blockchain.get_balance(alice)}")
    print(f"💰 Bob: {blockchain.get_balance(bob)}")
    print(f"💰 Charlie: {blockchain.get_balance(charlie)}")
    
    # Display blockchain
    blockchain.print_chain()
    
    # Verify integrity
    print("🔍 Verifying blockchain integrity...")
    if blockchain.is_chain_valid():
        print("✅ Blockchain is VALID!")
    else:
        print("❌ Blockchain is INVALID!")
    
    print("\n" + "="*60)
    print("🎉 TEST COMPLETE!")
    print("="*60 + "\n")