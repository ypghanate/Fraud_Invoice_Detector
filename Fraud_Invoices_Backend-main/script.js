const invoiceForm = document.getElementById('invoice-form');
const errorText = document.getElementById('errorText'); 

invoiceForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const vendor_name = document.getElementById('vendor_nameBox').value;
    const tax_id = document.getElementById('tax_idBox').value;
    const amount = document.getElementById('amount').value;
    const vendor_wallet_address = document.getElementById('vendor_wallet_addressBox').value;
    const description = document.getElementById('descriptionBox').value;

    const payload = { vendor_name, tax_id, amount, description, vendor_wallet_address };

    if (payload.amount <= 0 || !payload.vendor_name) {
        errorText.innerHTML = 'Invalid Data';
        return; 
    } 

    if (payload.vendor_wallet_address.slice(0, 2) !== '0x' || payload.vendor_wallet_address.length !== 42) {
        errorText.innerHTML = 'Incorrect W3 formatting';
        return;
    }

    errorText.innerHTML = '';

    try {
        const response = await fetch('http://127.0.0.1:8000/api/invoices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Server returned an error status');
        }

        const mLresponse = await response.json();

        const table = document.getElementById('table');
        const newRow = document.createElement('tr');
        
        newRow.innerHTML = `
            <td>${mLresponse.vendor_name}</td>
            <td>${mLresponse.amount}</td>
            <td>${mLresponse.status || 'pending'}</td>
        `;

        table.appendChild(newRow);

        invoiceForm.reset();

    } catch (mLerror) {
        errorText.innerHTML = 'Something wrong with fetching';
    }
});