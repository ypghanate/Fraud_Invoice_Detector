# Invoice Fraud Detection System

A full-stack invoice submission app with ML-based fraud scoring — a Node/Express +
MySQL transactional backend, paired with a standalone Python/Flask microservice that
runs an anomaly-detection model against each invoice.

---

## What it does

1. A user submits an invoice through a web form (vendor name, tax ID, amount,
   description, wallet address).
2. **Node/Express** validates the input and inserts it into **MySQL**.
3. Node queries MySQL for that vendor's historical average invoice amount and standard
   deviation, then calls a separate **Flask** microservice with those stats.
4. Flask runs the invoice through a pre-trained **scikit-learn `IsolationForest`**
   model and returns an anomaly score (`1` = normal, `-1` = anomalous).
5. Node merges the invoice record and the fraud score into one JSON response, which
   the frontend renders as a new table row.

A second, **not-yet-integrated** model — a fine-tuned **DistilBERT** text classifier —
exists to score the invoice *description* field for fraud language, but isn't wired
into the live request path yet.

---

## Architecture

Browser (index.html + script.js)
   → POST → Node/Express `app.js` (port 3000)
       - validates input
       - writes to MySQL
       - queries vendor stats
       - calls Flask
   → POST → Flask ML microservice `app.py` (port 8000)
       - loads pre-trained IsolationForest
       - builds z_score_amount / vendor_freq features
       - returns fraud_score

| Service | Port | Role |
|---|---|---|
| Node/Express (`app.js`) | `3000` | Owns the API, MySQL, and the frontend static files |
| Flask (`app.py`) | `8000` | Stateless inference only — no DB, no auth, called server-to-server by Node |

---

## Tech stack (specifics)

### Frontend
- Vanilla HTML/CSS/JS, no framework or bundler
- `fetch` API for the single `POST /api/invoices` call

### Backend / API (Node)
- **Node.js** (v18+, relies on the built-in global `fetch`)
- **Express** — routing, static file serving, JSON body parsing (`express.json()`)
- **`mysql2/promise`** — connection pooling, parameterized queries (`?` placeholders)

### Database
- **MySQL**, single table `invoices`:
```sql
  CREATE TABLE invoices (
      id INT AUTO_INCREMENT PRIMARY KEY,
      vendor_name VARCHAR(255) NOT NULL,
      tax_id VARCHAR(100),
      amount DECIMAL(12, 2) DEFAULT 0.00,
      description TEXT,
      vendor_wallet_address VARCHAR(255) NOT NULL,
      status VARCHAR(50) DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
```

### ML microservice (numeric fraud scoring — live)
- **Python** + **Flask**
- **scikit-learn** `sklearn.ensemble.IsolationForest`
```python
  IsolationForest(
      n_estimators=100,
      contamination=0.01,
      max_samples='auto',
      max_features=1.0,
      random_state=42,
  )
```
  - `contamination=0.01` = model expects ~1% of training data to be anomalous
  - Features: `z_score_amount`, `vendor_freq`
- **pandas** — feature-frame construction
- **joblib** — persists/loads the fitted model (`fraud_model.joblib`,
  `vendor_freq.joblib`)
- **Hugging Face `datasets`** — `purulalwani/Synthetic-Financial-Datasets-For-Fraud-Detection`

### Text classifier (NLP — trained, not yet integrated)
- **Hugging Face `transformers`**, base model **`distilbert-base-uncased`**
```python
  AutoTokenizer.from_pretrained("distilbert-base-uncased")
  AutoModelForSequenceClassification.from_pretrained(
      "distilbert-base-uncased", num_labels=2
  )
```
  - Binary sequence classification (fraud / not fraud) — not sentiment analysis
  - Fine-tuned with `Trainer` / `TrainingArguments`:
```python
    TrainingArguments(
        output_dir="distilbert-finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        bf16=False,
        learning_rate=2e-5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
    )
```
  - Metric: macro F1 (handles class imbalance)
  - Training data: `amitkedia/Financial-Fraud-Dataset`
  - Saved to `my_model_path/`
  - **Status:** trained, but not loaded by `app.py` yet

---

## Setup — do this yourself

### Prerequisites
- Node.js v18+
- Python 3.9+
- A running MySQL server

### 1. Install Node dependencies
```bash
npm init -y
npm install express mysql2
```

### 2. Install Python dependencies
```bash
pip install flask pandas scikit-learn joblib datasets
pip install torch transformers   # only for the DistilBERT classifier
```

### 3. Configure the database connection
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=invoice_system
```

### 4. Train the fraud model (one-time)
```bash
python train_fraud_model.py
```

### 5. Start the Flask ML service
```bash
python app.py
```

### 6. Start the Node server (separate terminal)
```bash
node app.js
```

### 7. Open the app
Go to `http://localhost:3000` (this exact host, to avoid a CORS mismatch).

---

## How to use / work with this project

### Submitting an invoice (normal usage)

1. With both servers running, open `http://localhost:3000` in your browser.
2. Fill in the form:
   - **Vendor name** — required, non-empty
   - **Tax ID** — optional
   - **Amount** — required, must be a positive number
   - **Wallet address** — required, must match `0x` + 40 hex characters (42 total),
     e.g. `0x1234567890abcdef1234567890abcdef12345678`
   - **Description** — optional free text
3. Click submit. On success, a new row appears in the table showing vendor name,
   amount, status, and fraud score.
4. If the ML service is down or errors, the invoice still saves — the analysis field
   just shows a placeholder message instead of a score.

### Testing the API directly (without the UI)

Useful for debugging or scripting — bypasses the form entirely.

```bash
curl -X POST http://localhost:3000/api/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Acme Corp",
    "tax_id": "US-12345",
    "amount": 1200.50,
    "description": "Consulting services",
    "vendor_wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
  }'
```

You can also hit the Flask service directly (skipping Node/MySQL entirely) to test
the model in isolation:

```bash
curl -X POST http://127.0.0.1:8000/analyze-invoice \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Acme Corp",
    "tax_id": "US-12345",
    "amount": 1200.50,
    "average_amount": 950.2,
    "std_dev": 210.5,
    "description": "Consulting services",
    "vendor_wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
  }'
```

### Retraining the fraud model

Do this whenever you want to change the training data, sample size, or model
hyperparameters:

1. Edit `train_fraud_model.py` — e.g. change `SAMPLE_SIZE`, or the
   `IsolationForest(...)` parameters (like `contamination`).
2. Re-run it:
```bash
   python train_fraud_model.py
```
   This overwrites `fraud_model.joblib` and `vendor_freq.joblib`.
3. **Restart Flask** (`Ctrl+C`, then `python app.py` again) — it only loads the model
   once at startup, so it won't pick up a new one without a restart.

### Making code changes (things to remember)

- **Neither Node nor Flask auto-reloads.** After editing `app.js` or `app.py`, stop
  the process (`Ctrl+C`) and restart it, or your edits won't take effect even though
  they're saved to disk.
- **Check what's actually running** if something seems stuck on old behavior:
```bash
  ps aux | grep node
  ps aux | grep python
```
- Always load the app from `http://localhost:3000`, not `http://127.0.0.1:3000` —
  mixing the two triggers a CORS error even though it's the same machine.

### Debugging a failed request

1. Open browser DevTools → **Network tab**.
2. Submit the form, find the failing/red request.
3. Click it and check:
   - **Request URL** — confirms which server it actually hit
   - **Response** tab — shows the real error message from Node or Flask
4. Check both terminals (Node's and Flask's) for server-side logs/tracebacks — most
   errors print there, not just in the browser.

### Extending this project

- **Persist the fraud score**: add a `fraud_score` column to `invoices`, and save
  `mlResult.fraud_score` in Node's insert logic.
- **Wire in the DistilBERT classifier**: load `my_model_path/` in `app.py`, run the
  invoice `description` through it, and combine its output with the IsolationForest
  score (e.g. flag as fraud if either model disagrees with "normal").
- **Add auth**: neither `/api/invoices` nor `/analyze-invoice` currently require any
  credentials — add an API key or session check before exposing this beyond localhost.

---

## API reference

### `POST /api/invoices` — Node, port 3000

Request:
```json
{
  "vendor_name": "Acme Corp",
  "tax_id": "US-12345",
  "amount": 1200.50,
  "description": "Consulting services",
  "vendor_wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
}
```

Response (`201`):
```json
{
  "invoice_id": 11,
  "vendor_name": "Acme Corp",
  "status": "pending",
  "stats": { "average_amount": 950.2, "std_dev": 210.5 },
  "analysis": { "fraud_score": 1 }
}
```

### `POST /analyze-invoice` — Flask, port 8000 (internal only)

Request:
```json
{
  "vendor_name": "Acme Corp",
  "amount": 1200.50,
  "average_amount": 950.2,
  "std_dev": 210.5,
  "description": "Consulting services"
}
```

Response:
```json
{
  "vendor_name": "Acme Corp",
  "amount": 1200.50,
  "vendor_freq": 1,
  "fraud_score": 1
}
```

---

## Known limitations / next steps

- **Vendor name mismatch**: `vendor_freq` falls back to `1` for real vendors, since
  the model trained on synthetic vendor IDs.
- **DistilBERT classifier isn't live**: trained but never loaded by `app.py`.
- **`fraud_score` isn't persisted** to the `invoices` table.
- **No authentication** on either service.
