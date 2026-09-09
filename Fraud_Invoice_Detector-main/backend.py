import os
import optuna
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
)
import evaluate
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = os.path.join(BASE_DIR, "nlp_model")

# 1. Load Dataset
dataset = load_dataset("amitkedia/Financial-Fraud-Dataset")

# 2. Tokenization
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 3. Define Evaluation Metric
metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels, average="macro")

# 4. Model Initialization Function for Optuna
def model_init():
    return AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2
    )

# 5. Define Search Space
def optuna_hp_space(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True),
        "per_device_train_batch_size": trial.suggest_categorical(
            "per_device_train_batch_size", [2, 4, 8]
        ),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 2, 4),
        "weight_decay": trial.suggest_float("weight_decay", 0.0, 0.1),
    }

# 6. Trainer Setup
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    fp16=torch.cuda.is_available(),
    logging_steps=10,
)

trainer = Trainer(
    model_init=model_init,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    processing_class=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    compute_metrics=compute_metrics,
)

# 7. Execute Hyperparameter Search via Optuna
best_run = trainer.hyperparameter_search(
    hp_space=optuna_hp_space,
    backend="optuna",
    n_trials=10,
    direction="maximize",
    compute_objective=lambda metrics: metrics["eval_f1"],
)

# 8. Train Final Model using Best Parameters
for n, v in best_run.hyperparameters.items():
    setattr(trainer.args, n, v)

trainer.train()

# 9. Save Best Fine-Tuned Model & Tokenizer
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)