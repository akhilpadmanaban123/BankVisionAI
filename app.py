from flask import Flask, render_template, request, jsonify
from database import Database
from gemini import process_natural_language_query
import json

app = Flask(__name__)
db = Database()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Process natural language query with enhanced Gemini
    result = process_natural_language_query(query)
    
    try:
        if result['type'] == 'customer_search':
            customers = db.get_customers(
                branch=result['parameters'].get('branch'),
                name=result['parameters'].get('name'),
                limit=result.get('limit')
            )
            if customers:
                return render_template('customers_list.html', 
                                     customers=customers,
                                     search_term=query)
        
        elif result['type'] == 'transaction_search':
            if 'account_number' in result['parameters']:
                transactions = db.get_transactions(
                    account_number=result['parameters']['account_number'],
                    limit=result.get('limit')
                )
            else:
                # If no account number, try to find by name
                customer = db.get_customer_by_name(
                    result['parameters'].get('name'),
                    result['parameters'].get('branch')
                )
                if customer:
                    transactions = db.get_transactions(
                        customer['account_number'],
                        limit=result.get('limit')
                    )
            
            if transactions:
                return render_template('transactions.html',
                                    transactions=transactions,
                                    customer_name=result['parameters'].get('name', 'Unknown'))
        
        elif result['type'] == 'combined_search':
            customer = db.get_customer_by_name(
                result['parameters'].get('name'),
                result['parameters'].get('branch')
            )
            if customer:
                transactions = db.get_transactions(
                    customer['account_number'],
                    limit=result.get('limit')
                )
                return render_template('customer.html',
                                    customer=customer,
                                    transactions=transactions)
    
    except Exception as e:
        print(f"Error processing query: {e}")
    
    return render_template('dashboard.html', error="No results found")

@app.route('/api/customers', methods=['GET'])
def get_customers():
    branch = request.args.get('branch')
    customers = db.get_customers(branch)
    return jsonify(customers)

@app.route('/api/transactions', methods=['GET'])
def get_transactions_api():
    account_number = request.args.get('account_number')
    transactions = db.get_transactions(account_number)
    return jsonify(transactions)

@app.route('/generate-sample-data', methods=['POST'])
def generate_sample_data():
    count = int(request.form.get('count', 10))
    db.generate_sample_data(count)
    return jsonify({"status": "success", "message": f"Generated {count} sample records"})

if __name__ == '__main__':
    app.run(debug=True)
