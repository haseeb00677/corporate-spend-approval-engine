# 💳 Corporate Spend Approval Engine

A scalable financial transaction approval system designed to simulate the backend logic of modern fintech platforms like **Brex** or **Ramp**. This engine handles expense routing, automated policy enforcement, and basic fraud detection.

## 🚀 Key Features

*   **Dynamic Approval Routing:**
    *   `<$50`: Auto-approved by system (Low risk).
    *   `$50 - $500`: Routed to **Manager** for review.
    *   `>$500`: Escalated to **VP of Finance** for multi-tier approval.
*   **Fraud Detection:** automatically flags and rejects duplicate transactions (same user, amount, and merchant) to prevent double-spending.
*   **Audit Logging:** Maintains an immutable JSON log of all transaction attempts for compliance.

## 🛠 Tech Stack
*   **Language:** Python 3.10+
*   **Framework:** Flask (REST API)
*   **Database:** In-Memory List (Scalable to PostgreSQL/SQLite)

## 💻 How to Run Locally

1. **Clone the repo:**
   ```bash
   git clone https://github.com/haseeb00677/corporate-spend-approval-engine.git
   cd corporate-spend-approval-engine
