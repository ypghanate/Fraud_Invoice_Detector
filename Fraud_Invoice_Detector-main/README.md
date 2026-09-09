# Invoice Fraud Detection System

A full-stack invoice submission application with **ML-based fraud scoring** — a Node.js/Express + MySQL transactional backend paired with a standalone Python/Flask microservice that runs a fine-tuned NLP text-classification model against each invoice description.

## What It Does

1. User submits an invoice via the web form with:

   * Vendor name
   * Tax ID
   * Amount
   * Invoice description
   * Vendor wallet address

2. Node.js/Express validates the input and inserts the invoice into MySQL.

3. Node.js calls the Flask ML microservice with the invoice description.

4. Flask runs the description through a fine-tuned **DistilBERT** text classifier and returns a fraud probability.

5. Node.js combines the invoice record and ML fraud analysis into a JSON response.

6. The frontend displays the invoice information and fraud assessment dynamically.

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
│       Python / Flask          │
│          Port 5001            │
│                               │
│  • Loads fine-tuned model     │
│  • Processes invoice text     │
│  • Runs DistilBERT inference  │
│  • Calculates fraud score     │
│  • Returns flag status        │
└───────────────┬───────────────┘
                │
                ▼
       ┌──────────────────┐
       │ Fine-Tuned       │
       │ DistilBERT Model │
       └──────────────────┘
```

## Tech Stack

### Frontend

* **HTML5**
* **CSS3**
* **Vanilla JavaScript**
* Browser **Fetch API**
* No frontend framework or bundler

The frontend communicates with the Node.js backend using REST API requests.

### Backend / API

* **Node.js v18+**
* **Express.js**
* **mysql2/promise**
* Native Node.js `fetch`
* RESTful API architecture
* Parameterized SQL queries

Node.js is responsible for:

* Receiving invoice submissions
* Validating user input
* Persisting invoice records
* Communicating with the ML microservice
* Returning the combined invoice and fraud analysis
* Serving the frontend application

### Database

The application uses **MySQL** for persistent invoice storage.

#### Database Schema

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
```

### Machine Learning

* **Python 3.9+**
* **PyTorch**
* **Hugging Face Transformers**
* **DistilBERT**
* **Flask**
* **Optuna**
* **Hugging Face Datasets**
* **Evaluate**
* **Pandas**

The fraud detection model is a fine-tuned `distilbert-base-uncased` binary sequence classifier.

## Hyperparameter Optimisation

Optuna is integrated with the Hugging Face `Trainer.hyperparameter_search` framework to automatically explore different training configurations.

The optimisation searches across:

* Learning rate
* Training batch size
* Number of training epochs
* Weight decay

## Model Evaluation

The primary evaluation metric is **Macro F1-score**.

Macro F1 calculates the F1-score independently for each class and then takes the average. This is useful for fraud detection because it reduces the effect of class imbalance and ensures that performance across both fraud and normal invoices is considered.

The model is evaluated across both:

* Fraudulent invoices
* Normal invoices

## Key Features

### Full-Stack Architecture

The system separates the transactional backend from the machine learning inference service.

* **Node.js/Express** handles application logic and database operations.
* **Python/Flask** handles machine learning inference.
* **MySQL** provides persistent storage.
* The frontend communicates with the backend using REST APIs.

### NLP-Based Fraud Detection

The system uses a fine-tuned **DistilBERT** model to classify invoice descriptions.

The model produces a fraud probability that is used to determine whether an invoice should be flagged.

### Hyperparameter Optimisation

**Optuna** is used to automatically search for effective training configurations.

The optimisation process considers:

* Learning rate
* Batch size
* Number of epochs
* Weight decay

### Microservice Architecture

The machine learning model runs independently from the Node.js application.

```text
Node.js Backend
       │
       │ POST /analyze/invoice
       ▼
Python Flask Service
       │
       ▼
DistilBERT Model
       │
       ▼
Fraud Probability
```

### Persistent Storage

Invoice information is stored in MySQL, allowing submitted invoices and their associated metadata to be persisted.

### Parameterized Database Queries

The backend uses parameterized SQL queries to reduce the risk of SQL injection attacks.

### Real-Time Analysis

Each invoice is analysed by the ML service during submission, allowing the frontend to immediately display the resulting fraud assessment.

## Technologies Used

| Component                   | Technology                |
| --------------------------- | ------------------------- |
| Frontend                    | HTML5, CSS3, JavaScript   |
| Backend                     | Node.js, Express.js       |
| Database                    | MySQL                     |
| Database Driver             | mysql2/promise            |
| ML Service                  | Python, Flask             |
| Deep Learning               | PyTorch                   |
| NLP                         | Hugging Face Transformers |
| NLP Model                   | DistilBERT                |
| Hyperparameter Optimisation | Optuna                    |
| Dataset                     | Financial-Fraud-Dataset   |
| ML Evaluation               | Macro F1-score            |
| API Communication           | REST / JSON               |

## Setup Instructions

### Prerequisites

* Node.js v18 or later
* Python 3.9 or later
* MySQL Server
* pip

### 1. Install Node.js Dependencies

```bash
npm init -y
```

```bash
npm install express mysql2
```

### 2. Install Python Dependencies

```bash
pip install flask pandas torch transformers optuna datasets evaluate
```

### 3. Configure Environment Variables

Linux/macOS:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=invoice_system
```

Windows PowerShell:

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="yourpassword"
$env:DB_NAME="invoice_system"
```

### 4. Fine-Tune the NLP Model

```bash
python train_text_model.py
```

The training process:

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

### 5. Start the Flask ML Service

```bash
python app.py
```

The Flask service runs on:

```text
http://localhost:5001
```

Endpoint:

```text
POST /analyze/invoice
```

### 6. Start the Node.js API Server

```bash
node app.js
```

Node.js runs on:

```text
http://localhost:3000
```

### 7. Access the Application

Open:

```text
http://localhost:3000
```

The browser loads the frontend application, which communicates with the Node.js API.

## API Reference

### POST `/api/invoices`

Creates a new invoice and performs fraud analysis.

**Backend:** Node.js / Express
**Port:** `3000`

#### Request Body

```json
{
    "vendor_name": "Example Vendor",
    "tax_id": "GB123456789",
    "amount": 1250.50,
    "description": "Payment for consulting services",
    "vendor_wallet_address": "0x123456789"
}
```

#### Response

```json
{
    "invoice_id": 1,
    "vendor_name": "Example Vendor",
    "status": "pending",
    "analysis": {
        "nlp_fraud_probability": 0.12,
        "is_flagged": false
    }
}
```

### POST `/analyze/invoice`

Sends an invoice description directly to the machine learning service.

**Service:** Python / Flask
**Port:** `5001`

#### Request Body

```json
{
    "description": "Payment for consulting services"
}
```

#### Response

```json
{
    "description": "Payment for consulting services",
    "scoring_method": "fine_tuned_distilbert_nlp",
    "scores": {
        "nlp_fraud_probability": 0.12
    },
    "is_flagged": false
}
```

## End-to-End Request Flow

1. The user submits an invoice through the frontend.
2. The frontend sends the invoice data to `POST /api/invoices`.
3. Node.js validates the submitted fields.
4. Node.js inserts the invoice into MySQL using a parameterized SQL query.
5. Node.js sends the invoice description to the Flask ML service.
6. Flask tokenizes the description using the DistilBERT tokenizer.
7. The fine-tuned DistilBERT model performs inference.
8. The model calculates the probability associated with the fraud class.
9. Flask returns the fraud probability and flag status.
10. Node.js combines the database record and ML analysis.
11. The final JSON response is returned to the frontend.
12. The frontend dynamically displays the invoice and fraud assessment.

```text
User
 │
 ▼
Frontend
 │
 │ POST /api/invoices
 ▼
Node.js / Express
 │
 ├──────────────► MySQL
 │                 │
 │                 └── Store Invoice
 │
 │ POST /analyze/invoice
 ▼
Flask ML Service
 │
 ▼
DistilBERT
 │
 ▼
Fraud Probability
 │
 ▼
Node.js
 │
 ▼
Frontend
 │
 ▼
Fraud Assessment
```

## Project Structure

```text
invoice-fraud-detector/
│
├── app.js
├── app.py
├── train_text_model.py
│
├── package.json
├── package-lock.json
│
├── index.html
├── script.js
├── style.css
│
├── nlp_model/
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── ...
│
└── README.md
```

## Summary

The Invoice Fraud Detection System combines a traditional transactional web application with a machine learning microservice.

The **Node.js/Express backend** manages invoice submissions, validation, database storage and API communication, while the **Python/Flask service** performs NLP-based fraud detection using a fine-tuned **DistilBERT** model.

This separation provides a modular architecture in which the machine learning component can be independently trained, evaluated and deployed without tightly coupling it to the main application.

The result is a full-stack application capable of accepting invoice submissions, analysing invoice descriptions using NLP and returning a real-time fraud risk assessment.
