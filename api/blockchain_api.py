"""
QuantumShield REST API
Provides HTTP endpoints for blockchain interaction
"""

from flask import Flask, request, jsonify
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blockchain.blockchain import Blockchain
from ai_security.anomaly_detector import AnomalyDetector

# Initialize Flask app
app = Flask(__name__)

# Initialize blockchain and AI detector
blockchain = Blockchain()
detector = AnomalyDetector(sensitivity=0.75)

# Store for wallets (in production, use a database)
wallets = {}

print("🚀 QuantumShield API Server Starting...")
print("="*60)


@app.route('/')
def home():
    """API home page"""
    return jsonify({
        'name': 'QuantumShield API',
        'version': '0.1.0',
        'description': 'Quantum-safe blockchain with AI security',
        'endpoints': {
            '/api/status': 'Get blockchain status',
            '/api/wallet/create': 'Create new wallet',
            '/api/wallet/balance/<address>': 'Get wallet balance',
            '/api/transaction/send': 'Send transaction',
            '/api/block/mine': 'Mine new block',
            '/api/chain': 'Get full blockchain',
            '/api/security/check': 'Check transaction security'
        }
    })


@app.route('/api/status')
def get_status():
    """Get blockchain status"""
    chain_info = blockchain.get_chain_info()
    
    return jsonify({
        'status': 'online',
        'blockchain': {
            'blocks': chain_info['blocks'],
            'total_transactions': chain_info['total_transactions'],
            'difficulty': chain_info['difficulty'],
            'is_valid': blockchain.is_chain_valid()
        },
        'ai_security': detector.get_statistics(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/wallet/create', methods=['POST'])
def create_wallet():
    """Create a new wallet"""
    data = request.get_json() or {}
    name = data.get('name', f'wallet_{len(wallets)}')
    
    # Create wallet
    address = blockchain.create_wallet(name)
    wallet_info = blockchain.wallets[address]
    
    # Store in API wallets dict
    wallets[name] = address
    
    return jsonify({
        'success': True,
        'wallet': {
            'name': name,
            'address': address
        },
        'message': f'Wallet "{name}" created successfully'
    }), 201


@app.route('/api/wallet/balance/<address>')
def get_balance(address):
    """Get wallet balance"""
    balance = blockchain.get_balance(address)
    
    return jsonify({
        'address': address,
        'balance': balance,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/transaction/send', methods=['POST'])
def send_transaction():
    """Send a transaction"""
    data = request.get_json()
    
    # Validate input
    required = ['sender_name', 'recipient', 'amount']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: sender_name, recipient, amount'
        }), 400
    
    sender_name = data['sender_name']
    recipient = data['recipient']
    amount = float(data['amount'])
    
    # Get sender wallet
    if sender_name not in wallets:
        return jsonify({
            'success': False,
            'error': f'Wallet "{sender_name}" not found'
        }), 404
    
    sender_wallet = wallets[sender_name]
    
    # Create and add transaction
    try:
        tx = blockchain.create_transaction(
            sender_wallet,
            recipient,
            amount
        )
        
        # Check with AI security
        is_anomaly, confidence, reason = detector.predict(tx)
        
        if is_anomaly:
            return jsonify({
                'success': False,
                'error': 'Transaction flagged by AI security',
                'security': {
                    'is_anomaly': is_anomaly,
                    'confidence': confidence,
                    'reason': reason
                }
            }), 403
        
        # Add to pending
        blockchain.add_transaction(tx)
        
        return jsonify({
            'success': True,
            'transaction': {
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            },
            'security': {
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'reason': reason
            },
            'message': 'Transaction added to pending pool'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/block/mine', methods=['POST'])
def mine_block():
    """Mine a new block"""
    data = request.get_json()
    miner_address = data.get('miner_address')
    
    if not miner_address:
        return jsonify({
            'success': False,
            'error': 'miner_address required'
        }), 400
    
    # Mine block
    try:
        new_block = blockchain.mine_pending_transactions(miner_address)
        
        return jsonify({
            'success': True,
            'block': {
                'index': new_block.index,
                'transactions': len(new_block.transactions),
                'hash': new_block.hash,
                'nonce': new_block.nonce,
                'timestamp': new_block.timestamp
            },
            'message': f'Block #{new_block.index} mined successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chain')
def get_chain():
    """Get the full blockchain"""
    chain_data = []
    
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': len(block.transactions),
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce
        })
    
    return jsonify({
        'length': len(blockchain.chain),
        'chain': chain_data,
        'is_valid': blockchain.is_chain_valid()
    })


@app.route('/api/security/check', methods=['POST'])
def check_security():
    """Check a transaction with AI security"""
    data = request.get_json()
    
    # Create dummy transaction for checking
    from blockchain.block import Transaction
    
    tx = Transaction(
        sender=data.get('sender', 'unknown'),
        recipient=data.get('recipient', 'unknown'),
        amount=float(data.get('amount', 0))
    )
    
    is_anomaly, confidence, reason = detector.predict(tx)
    
    return jsonify({
        'is_anomaly': is_anomaly,
        'confidence': confidence,
        'reason': reason,
        'recommendation': 'BLOCK' if is_anomaly else 'ALLOW'
    })


if __name__ == '__main__':
    print("✅ QuantumShield API Ready!")
    print("="*60)
    print("📍 Running on: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)