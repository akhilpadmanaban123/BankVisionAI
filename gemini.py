import requests
import re
import json

API_KEY = "your api key"
MODEL = "gemini-2.0-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def generate_gemini_response(prompt):
    headers = { "Content-Type": "application/json" }
    data = {
        "contents": [
            { "parts": [ { "text": prompt } ] }
        ],
        "generationConfig": {
            "temperature": 0.2,  # Lower temperature for more deterministic output
            "topP": 0.8
        }
    }

    response = requests.post(URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def process_natural_language_query(query):
    database_schema = """
    Database Schema:
    - Table: customers
      Columns: id, account_number (unique), name, branch, balance, account_type, opened_date, last_updated
    - Table: transactions
      Columns: id, transaction_id (unique), account_number (references customers), amount, 
               transaction_type (credit/debit), description, atm_id, transaction_date, balance_after
    """

    prompt = f"""
    {database_schema}

    Analyze this banking query and determine the exact database operation needed. 
    Respond with JSON containing:
    - "type": "customer_search", "transaction_search", or "combined_search"
    - "parameters": dictionary of relevant filters
    - "limit": number of results to return (if specified)
    - "sort": sorting preference if mentioned

    Examples:
    1. Query: "Show all customers from Palakkad branch"
    Output: {{
        "type": "customer_search",
        "parameters": {{"branch": "Palakkad"}},
        "limit": null,
        "sort": null
    }}

    2. Query: "Get last 5 transactions of account 123456789"
    Output: {{
        "type": "transaction_search",
        "parameters": {{"account_number": "123456789"}},
        "limit": 5,
        "sort": "transaction_date DESC"
    }}

    3. Query: "Show Arun Kumar's details and transactions"
    Output: {{
        "type": "combined_search",
        "parameters": {{"name": "Arun Kumar"}},
        "limit": null,
        "sort": null
    }}

    Current Query: {query}

    Respond ONLY with valid JSON. Do not include any explanatory text.
    """

    response = generate_gemini_response(prompt)
    
    try:
        result = json.loads(response)
        
        # Add validation for the result structure
        if not all(key in result for key in ['type', 'parameters']):
            raise ValueError("Invalid response structure")
            
        return result
        
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # Fallback to simple regex parsing
        return parse_with_regex(query)

def parse_with_regex(query):
    """Fallback parsing when Gemini response fails"""
    name_match = re.search(r'(\b[A-Z][a-z]+ [A-Z][a-z]+\b)', query)
    branch_match = re.search(r'\b(Palakkad|Kochi|Trivandrum|Kozhikode|Bangalore)\b', query, re.I)
    account_match = re.search(r'account (\d+)', query, re.I)
    limit_match = re.search(r'(last|recent) (\d+)', query, re.I)
    trans_match = re.search(r'\b(transactions?|history|statement)\b', query, re.I)
    #abduga
    result = {
        "type": "transaction_search" if trans_match else "customer_search",
        "parameters": {},
        "limit": int(limit_match.group(2)) if limit_match else None,
        "sort": "transaction_date DESC" if trans_match else None
    }
    
    if name_match:
        result['parameters']['name'] = name_match.group(1)
    if branch_match:
        result['parameters']['branch'] = branch_match.group(1)
    if account_match:
        result['parameters']['account_number'] = account_match.group(1)
    
    return result
