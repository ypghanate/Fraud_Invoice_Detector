const express = require('express');
const sqlite3 = require('sqlite3');
const app = express();
const PORT = 3000;
const path = require('path')

app.use(express.json());

app.use(express.static(__dirname));

const db = new sqlite3.Database('data.db', (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

db.run(`
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        tax_id TEXT,
        amount DECIMAL,
        description TEXT,
        vendor_wallet_address TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
`, (err) => {
    if (err) {
        console.error("Error creating table:", err.message);
    }
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/api/invoices', async (req, res) => {
    const { 
        vendor_name, 
        tax_id, 
        amount = 0, 
        description = '', 
        vendor_wallet_address 
    } = req.body;

    if (!vendor_name || !vendor_wallet_address) {
        return res.status(400).json({ error: "Missing required fields." });
    }

    const query = `
        INSERT INTO invoices (vendor_name, tax_id, amount, description, vendor_wallet_address, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    `;

    db.run(query, [vendor_name, tax_id, amount, description, vendor_wallet_address], async function(err) {
        if (err) {
            console.error("Database error:", err.message);
            return res.status(500).json({ error: "Database insertion failed" });
        }

        const invoiceId = this.lastID;
        let mlResult = null;
        const sendAt = new Date().toISOString()

        try {
            const mlResponse = await fetch('http://127.0.0.1:8000/analyze-invoice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }, 'Timestamp': sentAt,
                body: JSON.stringify({
                    invoice_id: invoiceId,
                    vendor_name,
                    tax_id,
                    amount,
                    description, 
                    vendor_wallet_address
                })
            });

            mlResult = await mlResponse.json();
        } catch (mlError) {
            console.warn("Stage 2 ML Engine is offline or failed:", mlError.message);
        }

        res.status(201).json({
            status: 'success',
            invoice_id: invoiceId,
            data: { vendor_name, tax_id, amount, description, vendor_wallet_address },
            analysis: mlResult || { message: "Analysis pending engine startup" }
        });
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});