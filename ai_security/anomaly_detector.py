"""
AI-Powered Anomaly Detection for Blockchain Security
Detects suspicious transactions and patterns
"""

import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from sklearn.ensemble import IsolationForest
import json
import sys
sys.path.append('..')
from blockchain.block import Transaction


class TransactionFeatureExtractor:
    """Extract features from transactions for AI analysis"""
    
    @staticmethod
    def extract_features(transaction) -> List[float]:
        """
        Extract numerical features from a transaction
        Returns: [amount, hour_of_day, sender_activity, recipient_activity]
        """
        # Amount (normalized)
        amount = float(transaction.amount)
        
        # Time features - hour of day (0-23)
        try:
            timestamp = datetime.fromisoformat(transaction.timestamp)
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
        except:
            hour = 12  # Default to midday
            day_of_week = 0
        
        # Create feature vector
        features = [
            amount,
            hour,
            day_of_week,
            len(transaction.sender),  # Address length as a feature
            len(transaction.recipient)
        ]
        
        return features


class AnomalyDetector:
    """AI-based anomaly detection for blockchain transactions"""
    
    def __init__(self, contamination=0.1, sensitivity=0.75):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of anomalies (0.1 = 10%)
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_trained = False
        self.sensitivity = sensitivity
        self.transaction_history = []
        self.anomaly_scores = []
        
        print(f"🤖 AI Anomaly Detector initialized (sensitivity: {sensitivity})")
    
    def train(self, transactions: List) -> bool:
        """
        Train the anomaly detection model on historical transactions
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            True if training successful
        """
        if len(transactions) < 10:
            print("⚠️  Need at least 10 transactions to train model")
            return False
        
        # Extract features
        features = []
        for tx in transactions:
            feature_vector = TransactionFeatureExtractor.extract_features(tx)
            features.append(feature_vector)
        
        # Convert to numpy array
        X = np.array(features)
        
        # Train model
        print(f"🔄 Training AI model on {len(transactions)} transactions...")
        self.model.fit(X)
        self.is_trained = True
        
        print("✅ AI model trained successfully!")
        return True
    
    def predict(self, transaction) -> Tuple[bool, float, str]:
        """
        Predict if a transaction is anomalous
        
        Args:
            transaction: Transaction object to analyze
            
        Returns:
            (is_anomaly, confidence_score, reason)
        """
        # Extract features
        features = TransactionFeatureExtractor.extract_features(transaction)
        X = np.array([features])
        
        # Predict
        if self.is_trained:
            # Use trained model
            prediction = self.model.predict(X)[0]
            score = self.model.score_samples(X)[0]
            
            # Normalize score to 0-1 range (higher = more suspicious)
            confidence = 1 / (1 + np.exp(score))  # Sigmoid transformation
            
            is_anomaly = prediction == -1
        else:
            # Use rule-based detection if not trained
            is_anomaly, confidence = self._rule_based_detection(transaction)
        
        # Generate reason
        reason = self._generate_reason(transaction, features, confidence)
        
        # Store in history
        self.transaction_history.append({
            'transaction': transaction,
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        return is_anomaly, confidence, reason
    
    def _rule_based_detection(self, transaction) -> Tuple[bool, float]:
        """Fallback rule-based detection when model isn't trained"""
        
        suspicious_score = 0.0
        
        # Rule 1: Very high amount
        if transaction.amount > 10000:
            suspicious_score += 0.4
        
        # Rule 2: Round numbers (often suspicious)
        if transaction.amount % 100 == 0:
            suspicious_score += 0.1
        
        # Rule 3: Very small amounts (spam)
        if transaction.amount < 0.01:
            suspicious_score += 0.3
        
        # Rule 4: Same sender and recipient
        if transaction.sender == transaction.recipient:
            suspicious_score += 0.5
        
        is_anomaly = suspicious_score > self.sensitivity
        
        return is_anomaly, min(suspicious_score, 1.0)
    
    def _generate_reason(self, transaction, features, confidence) -> str:
        """Generate human-readable reason for anomaly detection"""
        
        reasons = []
        
        # Check amount
        if transaction.amount > 10000:
            reasons.append("Unusually high transaction amount")
        elif transaction.amount < 0.01:
            reasons.append("Suspiciously low amount")
        
        # Check time
        hour = features[1]
        if hour < 6 or hour > 22:
            reasons.append("Transaction at unusual hour")
        
        # Check for round numbers
        if transaction.amount % 100 == 0:
            reasons.append("Round number amount (common in fraud)")
        
        # Check self-transfer
        if transaction.sender == transaction.recipient:
            reasons.append("Self-transfer detected")
        
        if not reasons:
            reasons.append("Pattern differs from normal behavior")
        
        return " | ".join(reasons)
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        
        if not self.transaction_history:
            return {
                'total_analyzed': 0,
                'anomalies_detected': 0,
                'anomaly_rate': 0.0
            }
        
        total = len(self.transaction_history)
        anomalies = sum(1 for tx in self.transaction_history if tx['is_anomaly'])
        
        return {
            'total_analyzed': total,
            'anomalies_detected': anomalies,
            'anomaly_rate': anomalies / total if total > 0 else 0.0,
            'average_confidence': np.mean([tx['confidence'] for tx in self.transaction_history])
        }
    
    def print_report(self):
        """Print detection report"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("🛡️  AI SECURITY REPORT")
        print("="*60)
        print(f"Total Transactions Analyzed: {stats['total_analyzed']}")
        print(f"Anomalies Detected: {stats['anomalies_detected']}")
        print(f"Anomaly Rate: {stats['anomaly_rate']*100:.2f}%")
        if stats['total_analyzed'] > 0:
            print(f"Average Confidence: {stats['average_confidence']:.2f}")
        print("="*60 + "\n")


# Test the module
if __name__ == "__main__":
    
    
    print("\n" + "="*60)
    print("🤖 TESTING AI ANOMALY DETECTOR")
    print("="*60 + "\n")
    
    # Create detector
    detector = AnomalyDetector(sensitivity=0.6)
    
    # Create normal transactions
    print("--- Creating Normal Transactions ---")
    normal_txs = [
        Transaction("Alice", "Bob", 50.0),
        Transaction("Bob", "Charlie", 75.5),
        Transaction("Charlie", "Alice", 30.0),
        Transaction("Alice", "Charlie", 45.25),
        Transaction("Bob", "Alice", 60.0),
        Transaction("Charlie", "Bob", 55.75),
        Transaction("Alice", "Bob", 40.0),
        Transaction("Bob", "Charlie", 65.5),
        Transaction("Charlie", "Alice", 35.0),
        Transaction("Alice", "Charlie", 50.0),
    ]
    
    # Train on normal transactions
    detector.train(normal_txs)
    
    # Create suspicious transactions
    print("\n--- Testing Suspicious Transactions ---")
    suspicious_txs = [
        Transaction("Alice", "Bob", 50000),  # Very high amount
        Transaction("Bob", "Bob", 100),      # Self-transfer
        Transaction("Charlie", "Alice", 0.001),  # Very low amount
        Transaction("Alice", "Charlie", 1000),   # Round number
    ]
    
    for tx in suspicious_txs:
        is_anomaly, confidence, reason = detector.predict(tx)
        
        status = "🚨 ANOMALY" if is_anomaly else "✅ NORMAL"
        print(f"\n{status}")
        print(f"   Transaction: {tx.sender[:8]}... → {tx.recipient[:8]}... : {tx.amount}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Reason: {reason}")
    
    # Print report
    detector.print_report()
    
    print("\n" + "="*60)
    print("✅ AI ANOMALY DETECTOR TEST COMPLETE!")
    print("="*60 + "\n")