import psycopg2
from psycopg2 import sql
import random
from datetime import datetime, timedelta
import names

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.jdsuuvmyrvfvuthrkdll",
            password="hArRyPoTtEr123$",
            host="aws-0-ap-south-1.pooler.supabase.com",
            port="5432"
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create customers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    account_number VARCHAR(20) UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    branch VARCHAR(50) NOT NULL,
                    balance DECIMAL(15, 2) DEFAULT 0.00,
                    account_type VARCHAR(20),
                    opened_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(30) UNIQUE,
                    account_number VARCHAR(20) REFERENCES customers(account_number),
                    amount DECIMAL(15, 2) NOT NULL,
                    transaction_type VARCHAR(10) CHECK (transaction_type IN ('credit', 'debit')),
                    description TEXT,
                    atm_id VARCHAR(20),
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    balance_after DECIMAL(15, 2)
                )
            """)
            
            self.conn.commit()

    def get_customer_by_name(self, name, branch=None):
        with self.conn.cursor() as cur:
            if branch:
                cur.execute("""
                    SELECT * FROM customers 
                    WHERE name ILIKE %s AND branch ILIKE %s 
                    LIMIT 1
                """, (f"%{name}%", f"%{branch}%"))
            else:
                cur.execute("""
                    SELECT * FROM customers 
                    WHERE name ILIKE %s 
                    LIMIT 1
                """, (f"%{name}%",))
            
            result = cur.fetchone()
            if result:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, result))
            return None

    def get_customers(self, branch=None, name=None, limit=None):
        with self.conn.cursor() as cur:
            query = "SELECT * FROM customers"
            params = []
            conditions = []
        
            if branch:
                conditions.append("branch ILIKE %s")
                params.append(f"%{branch}%")
            if name:
                conditions.append("name ILIKE %s")
                params.append(f"%{name}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query, params)
            results = cur.fetchall()
        
            if results:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in results]
            return []

    def get_transactions(self, account_number, limit=None):
        with self.conn.cursor() as cur:
            query = """
                SELECT * FROM transactions 
                WHERE account_number = %s 
                ORDER BY transaction_date DESC
            """
            params = [account_number]
        
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query, params)
            results = cur.fetchall()
        
            if results:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in results]
            return []

    def generate_sample_data(self, count=10):
        branches = ['Palakkad', 'Kochi', 'Trivandrum', 'Kozhikode', 'Bangalore']
        account_types = ['Savings', 'Current', 'Salary', 'NRI']
        
        with self.conn.cursor() as cur:
            # Clear existing data
            cur.execute("TRUNCATE TABLE customers, transactions RESTART IDENTITY")
            
            # Generate sample customers
            for _ in range(count):
                name = names.get_full_name()
                branch = random.choice(branches)
                account_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                balance = round(random.uniform(1000, 1000000), 2)
                account_type = random.choice(account_types)
                opened_date = datetime.now() - timedelta(days=random.randint(1, 365*5))
                
                cur.execute("""
                    INSERT INTO customers 
                    (account_number, name, branch, balance, account_type, opened_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (account_number, name, branch, balance, account_type, opened_date))
                
                # Generate sample transactions
                transaction_count = random.randint(5, 20)
                current_balance = balance
                
                for _ in range(transaction_count):
                    transaction_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                    amount = round(random.uniform(100, 10000), 2)
                    transaction_type = random.choice(['credit', 'debit'])
                    description = random.choice([
                        'ATM Withdrawal', 'Fund Transfer', 'UPI Payment', 
                        'Deposit', 'Online Purchase', 'Bill Payment'
                    ])
                    atm_id = ''.join([str(random.randint(0, 9)) for _ in range(8)]) if random.random() > 0.3 else None
                    transaction_date = datetime.now() - timedelta(days=random.randint(0, 30))
                    
                    if transaction_type == 'debit':
                        current_balance -= amount
                    else:
                        current_balance += amount
                    
                    cur.execute("""
                        INSERT INTO transactions 
                        (transaction_id, account_number, amount, transaction_type, 
                         description, atm_id, transaction_date, balance_after)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (transaction_id, account_number, amount, transaction_type, 
                          description, atm_id, transaction_date, current_balance))
            
            self.conn.commit()
