from flask import Flask, request, jsonify
from database import get_db_connection

app = Flask(__name__)

# --- BUSINESS RULES ---
AUTO_APPROVE_LIMIT = 50.00
VP_APPROVAL_LIMIT = 500.00

@app.route('/')
def home():
    return jsonify({
        "status": "Online",
        "system": "Corporate Spend Approval Engine v1.0",
        "database": "SQLite Connected"
    })

@app.route('/submit_expense', methods=['POST'])
def submit_expense():
    data = request.json
    
    # 1. Validation
    if not data or 'amount' not in data or 'merchant' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing required fields (amount, merchant, user_id)"}), 400

    amount = float(data['amount'])
    merchant = data['merchant']
    user_id = data['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Fraud Detection (Check for Duplicate)
    # Checks if this user submitted an expense for the same amount at same merchant recently
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE user_id = ? AND merchant = ? AND amount = ? AND status != 'REJECTED'
    ''', (user_id, merchant, amount))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({
            "status": "REJECTED",
            "reason": "Duplicate Transaction Detected - Fraud Alert"
        }), 403

    # 3. Approval Workflow Logic
    status = "PENDING"
    stage = "NONE"

    if amount < AUTO_APPROVE_LIMIT:
        status = "APPROVED"
        stage = "AUTO_SYSTEM"
    elif amount < VP_APPROVAL_LIMIT:
        status = "PENDING_MANAGER"
        stage = "MANAGER_REVIEW"
    else:
        status = "PENDING_VP"
        stage = "VP_FINANCE_REVIEW"

    # 4. Save to Database
    cursor.execute('''
        INSERT INTO expenses (user_id, merchant, amount, status, approval_stage)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, merchant, amount, status, stage))
    
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Expense Processed",
        "expense_id": expense_id,
        "status": status,
        "current_stage": stage
    }), 201

@app.route('/audit_logs', methods=['GET'])
def get_audit_logs():
    """Returns all transactions for compliance auditing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert database rows to list of dicts
    logs = [dict(row) for row in rows]
    return jsonify(logs)

@app.route('/approve/<int:expense_id>', methods=['POST'])
def manual_approve(expense_id):
    """Simulates a Manager or VP clicking 'Approve'"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE expenses SET status = "APPROVED", approval_stage = "COMPLETED" WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Expense {expense_id} has been manually approved."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
