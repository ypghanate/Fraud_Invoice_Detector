# Invoice Fraud Detection System

A full-stack invoice submission app with ML-based fraud scoring.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (`fetch` API)
- **Backend:** Node.js + Express
- **Database:** MySQL
- **ML Microservice:** Python + Flask + scikit-learn (`IsolationForest`)

## Architecture

Browser → Node/Express (port 3000) → MySQL
                    ↓
             Flask ML service (port 8000)

## Features

- Submit invoices via a web form
- Server-side validation of amount and wallet address
- Automatic fraud scoring per invoice
- Vendor-level average/std-dev stats stored in MySQL

## Setup

1. Install Node dependencies:
```bash
   npm install express mysql2
```

2. Install Python dependencies:
```bash
   pip install flask pandas scikit-learn joblib datasets
```

3. Train the fraud model *(one-time step)*:
```bash
   python train_fraud_model.py
```

4. Start the Flask ML service:
```bash
   python app.py
```

5. Start the Node server:
```bash
   node app.js
```

6. Open `http://localhost:3000` in your browser.

## API Endpoints

### `POST /api/invoices`
Creates an invoice and returns the fraud analysis.

**Request:**
```json
{
  "vendor_name": "Acme Corp",
  "tax_id": "US-12345",
  "amount": 1200.50,
  "description": "Consulting services",
  "vendor_wallet_address": "0x1234...abcd"
}
```

**Response:**
```json
{
  "invoice_id": 11,
  "status": "pending",
  "analysis": { "fraud_score": 1 }
}
```

## Notes

> Fraud score is computed but **not yet persisted** to the database.
> Vendor description text is **not yet** factored into the fraud score.

---
*Built with Node, Flask, and MySQL.*
