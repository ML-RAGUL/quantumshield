"""
QuantumShield Configuration
Post-Quantum Blockchain with AI Security
"""

import os

class Config:
    # Blockchain settings
    DIFFICULTY = 4  # Mining difficulty
    BLOCK_SIZE_LIMIT = 1000000  # 1MB
    
    # Post-Quantum Cryptography settings
    PQC_SIGNATURE_ALGORITHM = "Dilithium2"  # NIST standard
    PQC_KEM_ALGORITHM = "Kyber512"  # Key Encapsulation Mechanism
    
    # AI Security settings
    ANOMALY_THRESHOLD = 0.75  # Confidence threshold for anomaly detection
    MAX_TRANSACTION_VALUE = 1000000  # Maximum transaction value
    SUSPICIOUS_PATTERN_WINDOW = 100  # Number of transactions to analyze
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    DEBUG_MODE = True
    
    # Database (for now, in-memory)
    DATABASE_PATH = "blockchain_data.json"
    
    @staticmethod
    def get_version():
        return "QuantumShield v0.1.0-alpha"

# Global config instance
config = Config()