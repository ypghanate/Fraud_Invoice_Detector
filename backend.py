import os
import numpy as np
import pandas as pd
import joblib
import torch
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)

# Use absolute pathing based on backend.py directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "nlp_model")

FRAUD_THRESHOLD = 0.1

tokenizer = AutoTokenizer.from_pretrained(path)
model = AutoModelForSequenceClassification.from_pretrained(path)
model.eval()


def analyze_nlp_description(text: str) -> float:
    # 1. Tokenize text
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    
    # 2. DistilBERT does not use token_type_ids; remove if present
    inputs.pop("token_type_ids", None)

    # 3. Perform inference
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        
        # Assuming Index 1 corresponds to "fraudulent invoice"
        # Extract scalar value and convert from PyTorch tensor to Python float
        fraud_prob = float(probs[0][1].item())
        
    return fraud_prob


# ------------------------------------------------------------------
# 4. API Endpoints
# ------------------------------------------------------------------
@app.route('/analyze/invoice', methods=['POST'])
def analyze_transaction():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    description = str(data.get("description") or "")

    # Calculate NLP Fraud Probability
    nlp_score = analyze_nlp_description(description)
    print(f"Computed Fraud Probability: {nlp_score:.4f}")

    return jsonify({
        "description": description,
        "scoring_method": "deberta_v3_zero_shot_nlp_and_isolation_forest_ensemble",
        "scores": {
            "nlp_fraud_probability": round(nlp_score, 4),
        },
        "is_flagged": nlp_score >= FRAUD_THRESHOLD
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)