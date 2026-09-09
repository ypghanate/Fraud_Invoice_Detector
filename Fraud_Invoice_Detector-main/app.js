const express = require('express');
const mysql = require('mysql2/promise');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(__dirname));

const DB_NAME = process.env.DB_NAME || 'invoice_system';

const dbConfig = {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
};

// Global pool variable
let db;

async function initDb() {
    try {
        // 1. Connect without selecting a DB to create the database if missing
        const tempConn = await mysql.createConnection({
            host: dbConfig.host,
            user: dbConfig.user,
            password: dbConfig.password
        });

        await tempConn.query(`CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;`);
        await tempConn.end(); // Clean up temporary setup connection

        // 2. Initialize the connection pool pointing to the targeted database
        db = mysql.createPool(dbConfig);

        // 3. Create the table
        const createTableQuery = `
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vendor_name VARCHAR(255) NOT NULL,
                tax_id VARCHAR(100),
                amount DECIMAL(12, 2) DEFAULT 0.00,
                description TEXT,
                vendor_wallet_address VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        `;
        await db.query(createTableQuery);
        console.log(`✅ Connected to MySQL and initialized database '${DB_NAME}' and 'invoices' table.`);
    } catch (err) {
        console.error('❌ Error initializing MySQL database:', err.message);
    }
}

initDb();

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/api/invoices', async (req, res) => {
    console.log('RAW BODY:', req.body);
    const {
        vendor_name,
        tax_id,
        amount = 0,
        description = '',
        vendor_wallet_address
    } = req.body;

    if (!vendor_name || !vendor_wallet_address) {
        return res.status(400).json({ error: "Missing required fields: vendor_name and vendor_wallet_address" });
    }

    try {
        const insertQuery = `
            INSERT INTO invoices (vendor_name, tax_id, amount, description, vendor_wallet_address, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        `;
        const [insertResult] = await db.query(insertQuery, [
            vendor_name,
            tax_id || null,
            amount,
            description,
            vendor_wallet_address
        ]);

        const invoiceId = insertResult.insertId;
        const now = new Date();

        const mlFeatures = {
            amount: Number(amount)
        };

        let mlResult = null;

        try {
            const mlResponse = await fetch('http://127.0.0.1:5001/analyze/invoice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Timestamp': now.toISOString()
                },
                body: JSON.stringify({
                    invoice_id: invoiceId,
                    vendor_name,
                    tax_id,
                    description,
                    vendor_wallet_address,
                    ...mlFeatures
                })
            });

            if (mlResponse.ok) {
                mlResult = await mlResponse.json();
            } else {
                console.warn(`ML Engine HTTP Error: ${mlResponse.status}`);
            }
        } catch (mlError) {
            console.warn("Stage 2 ML Engine is offline or failed:", mlError.message);
        }

        return res.status(201).json({
            invoice_id: invoiceId,
            vendor_name,
            tax_id,
            amount,
            description,
            vendor_wallet_address,
            status: 'pending',
            features: mlFeatures,
            analysis: mlResult || { message: "Analysis pending engine startup" }
        });
    } catch (dbError) {
        console.error("Database error:", dbError.message);
        return res.status(500).json({ error: "Internal server error" });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});