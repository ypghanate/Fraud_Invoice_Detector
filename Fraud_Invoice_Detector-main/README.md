# Invoice Fraud Detection System

A full-stack invoice submission application with **ML-based fraud scoring** — a Node.js/Express + MySQL transactional backend paired with a standalone Python/Flask microservice that runs a fine-tuned NLP text-classification model against each invoice description.

---

## What It Does

1. A user submits an invoice through a web form containing:
   - Vendor name
   - Tax ID
   - Amount
   - Invoice description
   - Vendor wallet address

2. **Node.js/Express** validates the input and inserts the invoice into **MySQL**.

3. Node.js calls a separate **Flask ML microservice** with the invoice description.

4. Flask runs the description through a fine-tuned **DistilBERT** text-classification model and returns a fraud probability score.

5. Node.js combines the invoice record and ML fraud analysis into a JSON response.

6. The frontend receives the result and dynamically displays the invoice and fraud assessment in the interface.

---

## Architecture

```text
┌───────────────────────────────┐
│           Browser             │
│      index.html + script.js   │
└───────────────┬───────────────┘
                │
                │ POST /api/invoices
                ▼
┌───────────────────────────────┐
│       Node.js / Express       │
│          Port 3000            │
│                               │
│  • Validates invoice input    │
│  • Handles API requests       │
│  • Writes data to MySQL       │
│  • Calls Flask ML service     │
│  • Serves frontend files      │
└───────────┬───────────┬───────┘
            │           │
            │           │ SQL
            │           ▼
            │    ┌───────────────┐
            │    │     MySQL     │
            │    │   invoices    │
            │    └───────────────┘
            │
            │ POST /analyze/invoice
            ▼
┌───────────────────────────────┐
│       Python / Flask         │
│          Port 5001           │
│                              │
│  • Loads fine-tuned model    │
│  • Processes invoice text    │
│  • Runs DistilBERT inference │
│  • Calculates fraud score    │
│  • Returns flag status       │
└───────────────┬──────────────┘
                │
                ▼
       ┌──────────────────┐
       │ Fine-Tuned       │
       │ DistilBERT Model │
       └──────────────────┘

'''


# Tech Stack

## Frontend

- **HTML5**
- **CSS3**
- **Vanilla JavaScript**
- Browser **Fetch API**
- No frontend framework or bundler

The frontend communicates with the Node.js backend using REST API requests.

---

## Backend / API

- **Node.js v18+**
- **Express.js**
- **mysql2/promise**
- Native Node.js `fetch`
- RESTful API architecture
- Parameterized SQL queries

Node.js is responsible for:

- Receiving invoice submissions
- Validating user input
- Persisting invoice records
- Communicating with the ML microservice
- Returning the combined invoice and fraud analysis
- Serving the frontend application

---

## Database

The application uses **MySQL** for persistent invoice storage.

### Database Schema

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
);

# Hyperparameter Optimisation

Optuna is integrated with the Hugging Face `Trainer.hyperparameter_search` framework to automatically explore different training configurations.

The optimisation searches across:

- Learning rate
- Training batch size
- Number of training epochs
- Weight decay

---

# Model Evaluation

The primary evaluation metric is **Macro F1-score**.

Macro F1 calculates the F1-score independently for each class and then takes the average. This is useful for fraud detection because it reduces the effect of class imbalance and ensures that performance across both fraud and normal invoices is considered.

The model is evaluated across both:

- Fraudulent invoices
- Normal invoices




# Setup Instructions

## Prerequisites

Install the following before running the application:

- Node.js v18 or later
- Python 3.9 or later
- MySQL Server
- pip

## 1. Install Node.js Dependencies

Initialise the Node.js project:

```bash
npm init -y
```

Install the required packages:

```bash
npm install express mysql2
```

## 2. Install Python Dependencies

Install the ML and Flask dependencies:

```bash
pip install flask pandas torch transformers optuna datasets evaluate
```

## 3. Configure Environment Variables

Configure the MySQL database connection:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=invoice_system
```

On Windows PowerShell:

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="yourpassword"
$env:DB_NAME="invoice_system"
```

## 4. Fine-Tune the NLP Model

Run the training script:

```bash
python train_text_model.py
```

This performs the following steps:

1. Loads the financial fraud dataset.
2. Initialises the DistilBERT base model.
3. Creates the training configuration.
4. Runs Optuna hyperparameter optimisation.
5. Evaluates candidate models.
6. Selects the best hyperparameter configuration.
7. Fine-tunes DistilBERT using the selected configuration.
8. Saves the trained model and tokenizer.

The resulting model files are stored in:

```text
nlp_model/
```

## 5. Start the Flask ML Service

Open a terminal and run:

```bash
python app.py
```

The Flask service runs on:

```text
http://localhost:5001
```

The service exposes the following endpoint:

```text
POST /analyze/invoice
```

## 6. Start the Node.js API Server

Open a second terminal and run:

```bash
node app.js
```

The Node.js application runs on:

```text
http://localhost:3000
```

## 7. Access the Application

Open the following address in your browser:

```text
http://localhost:3000
```

The browser loads the frontend application, which communicates with the Node.js API.
