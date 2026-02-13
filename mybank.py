import secrets
import string 
import sqlite3
import uuid
import pickle
import numpy as np
def setup_database():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL,
            userid TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            account_number INTEGER UNIQUE,
            balance REAL DEFAULT 0.0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cibil_score INTEGER DEFAULT -1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transactionid TEXT NOT NULL UNIQUE,
            sender_username TEXT,
            sender_id TEXT,
            receiver_acc INTEGER,
            receiver_username TEXT,
            amount REAL,
            status TEXT DEFAULT 'failed',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

setup_database() # <--- CALLING THE FUNCTION

def cap(): #this function is for captcha generation
    cd = string.digits + string.ascii_letters
    return "".join(secrets.SystemRandom().choices(cd, k=6))

def accountnum(): #this function is for account number generation
    return int("".join(secrets.SystemRandom().choices(string.digits, k=10)))

def transactionid(): #this function is for transactionid generation
   return str(uuid.uuid4())

class Bank:
    def __init__(self, userid):
        self.userid = userid
        self.conn = sqlite3.connect("bank.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("SELECT balance FROM users WHERE userid = ?", (self.userid,))
        data = self.cursor.fetchone()
        if data:
            self.__balance = data[0]
        else:
            self.__balance = 0

    def save_to_db(self):
        self.cursor.execute("UPDATE users SET balance = ? WHERE userid = ?", (self.__balance, self.userid))
        self.conn.commit()

    def edit_profile(self):
        pass

    def balance(self):
        print(f"💰 Your current balance is: ₹{self.__balance}")

    def deposite(self):
        print("\n--- DEPOSITE MONEY ---")
        try:
            d = float(input("Amount to deposit: "))
            if d <1:
                print("Minimum deposit is 1")
            else:
                self.__balance += d
                self.save_to_db()
                print(f"Deposited! New Balance: ₹{self.__balance}")
        except ValueError:
            print("Invalid input.")

    def withdraw(self):
        print("\n--- WITHDRAW MONEY ---")
        try:
            w = float(input("Amount to withdraw: "))
            if w <1:
                print("Minimum withdraw is 1")
            elif w > self.__balance:
                print("Insufficient balance")
            else:
                self.__balance -= w
                self.save_to_db()
                print(f"Withdrawn! New Balance: ₹{self.__balance}")
        except ValueError:
            print("Invalid input.")

    def transfer(self):
        print("\n--- 💸 SEND MONEY ---")
        try:
            receiver_acc = int(input("Enter Receiver's Account Number: "))
            cursor = self.conn.cursor()

            # Check if Receiver Exists
            cursor.execute("SELECT username FROM users WHERE account_number = ?", (receiver_acc,))
            receiver_data = cursor.fetchone()
            cursor.execute("SELECT username,account_number FROM users WHERE userid= ?",(self.userid,))
            sender_data = cursor.fetchone()
            if not (receiver_data and sender_data):
                print(" Receiver Account Number not found.")
                return
            receiver_name =receiver_data[0] 
            sender_name=sender_data[0]
            if receiver_acc==sender_data[1]:
                print("self transfer not available")
                return
            print(f"found User: {receiver_name}")
            amount = float(input("Enter Amount to Transfer: "))
        except ValueError:
            print(" Invalid Input. Numbers only.")
            return

        # 1. Basic Checks
        if amount <= 0:
            print(" You cannot send 0 or negative money.")
            return
        
        if amount > self.__balance:
            print("Insufficient Balance.")
            return

        # 2. The Transaction
        try:
            # EXECUTE TRANSFER 
            # 1. Deduct from SENDER
            cursor.execute("UPDATE users SET balance = balance - ? WHERE userid = ?", (amount, self.userid))
            
            # 2. Add to RECEIVER
            cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, receiver_acc))
            
            # 3. Create Receipt for transaction
            cursor.execute("INSERT INTO transactions (transactionid,sender_username, sender_id, receiver_acc, receiver_username, amount ,status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
               (transactionid(),sender_name, self.userid, receiver_acc, receiver_name, amount,"✅ Success"))
            # 4. SAVE EVERYTHING
            self.conn.commit()
            
            # Update local variable
            self.__balance -= amount
            print(f"✅ Success! Sent ₹{amount} to {receiver_name}.")
            print(f"💰 Your New Balance: ₹{self.__balance}")

        except Exception as e:
            # EMERGENCY BUTTON: If anything crashes, UNDO EVERYTHING
            self.conn.rollback()
            print(f"❌ Transaction Failed. Money has been refunded. Error: {e}")

    def view_transactions(self):
        print("\n--- HISTORY ---")
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT sender_id,sender_username,receiver_username,amount,transactionid,date,status FROM transactions WHERE sender_id= ? OR sender_username = ?", (self.userid, self.userid))
            
            rows = cursor.fetchall()

            if not rows:
                print("No transactions found.")
            else:
                for row in rows:
                    if row[0]==self.userid:
                        print(f"SEND TO {row[2]} FROM {row[1]} AMOUNT {row[3]} TRANSACTION ID {row[4]} DATE {row[5]} STATUS {row[6]}")
                        print("\n")

                    else:
                        print(f"RECIEVE FROM {row[1]} RECIEVED {row[2]} AMOUNT {row[3]} TRANSACTION ID {row[4]} DATE {row[5]} STATUS {row[6]}")
                        print("\n")
        except Exception as e:
            print(f"Error occured while checking transactions {e}")

    def apply_for_loan(self):
        print("\n--- 🤖 AI LOAN APPROVAL ---")
        
        # 1. GATHER DATA
        current_bal = self.__balance
        
        # Count user's transactions from DB
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE sender_id = ?", (self.userid,))
        txn_count = cursor.fetchone()[0]
        
        print(f"📊 Analyzing: Balance=₹{current_bal} | Activity={txn_count} txns")

        # 2. LOAD BRAIN
        try:
            with open('loan_model.pkl', 'rb') as f:
                model = pickle.load(f)
        except FileNotFoundError:
            print("❌ Error: Brain missing. Run train_ai.py first.")
            return

        # 3. PREDICT
        # Reshape data: [[balance, txn_count]]
        features = np.array([[current_bal, txn_count]])
        prediction = model.predict(features)
        
        # 4. RESULT
        if prediction[0] == 1:
            print("✅ CONGRATULATIONS! Loan Approved by AI.")
        else:
            print("❌ REJECTED. AI suggests: Increase balance or use the app more.")

    def get_balance(self):
        return self.__balance 
    
class Loans(Bank):
    def __init__(self, userid, balance1):
        super().__init__(userid)
        self.balance1 = balance1
        self.interest_rate = 0.05

    def balance(self):
        try:
            interest1 = self.interest_rate * self.balance1
            total = interest1 + self.balance1
            print(f"📈 Total amount with 5% Interest: ₹{total}")
        except:
            print("Error occured while calculating intrest")

class Openaccount(Bank):
    def __init__(self, Username, Userid, Password,Balance1):
        self.Username = Username
        self.Userid=Userid
        self.Password = Password
        self.Balance1=Balance1
        
    def open_account(self):
        acc_num = accountnum()
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, userid, password, account_number,balance) VALUES (?, ?, ?, ?, ?)", 
                       (self.Username,self.Userid, self.Password, acc_num,self.Balance1))
            conn.commit()
            print(f"\n🎉 Account Created! User: {self.Username} | Acc No: {acc_num}")
        except sqlite3.IntegrityError:
            print(f"User ID '{self.Userid}' already exists.")
        except:
            print("Error occured while creating the account")
        finally:
            conn.close() 
#decorative function to handle login and home pages
def start(b):
    def login():
        try:
            print("\n--- LOGIN ---")
            userid_input = input("Enter user ID: ")
            password_input = input("Enter password: ")
            # --- Check Details From Database  ---
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE userid = ? AND password = ?", (userid_input, password_input))
            user_data = cursor.fetchone()
            if user_data:
                cursor.execute("SELECT username FROM users WHERE userid= ?",(userid_input,))
                username1=cursor.fetchone()[0]
                conn.close()
                # Captcha Logic
                m = cap()
                print(f"Captcha: {m}")
                c = input("Enter captcha: ")
                while True:
                    if c == m:
                        print(f"Welcome, {username1}!")
                        b(userid_input) # Go to Banking
                        break
                    else:
                        print("Wrong Captcha.")
                        m=cap()
                        print(f"Captcha: {m}")
                        c=input("Again Enter the captcha: ")
            else:
                print("Invalid User id or Password.")
                home() # Go back to start
        except RecursionError :
            print("Unable to login to the bank please refresh")
        except:
            print("Error occured while logging into the bank")
    def createac():
        try:
            print("\n--- CREATE ACCOUNT ---")
            A = input("Enter Full Name: ")
            A1=input("Enter User ID ")
            B = input("Enter Password: ")
            C = input("Re-Enter Password: ")
            D1=0
            if B == C:
                D = input("Would you like to deposite money right now if yes enter \"y\" if not enter \"n\": ")
                if D=="y":
                    D1=float(input("How much would you like to deposite: "))
                a1 = Openaccount(A, A1, B, D1)
                a1.open_account()
                home() # Go back to home to login
            else:
                print("Passwords did not match.")
                createac()
        except RecursionError:
            print("Too many attepts please refresh ")
        except:
            print("Error occured while creating the account")
    
    def home():
        try:
            print("\nWelcome to saiganesh bank \n")
            print("Press 'L' to Login")
            print("Press 'C' to Create Account")
            print("Press 'Q' to Quit")
            choice = input("Choice: ").upper()
            if choice == "L":
                login()
            elif choice == "C":
                createac()
            elif choice == "Q":
                print("Bye!")
            else:
                print("Invalid input")
                home()
        except RecursionError:
            print("Too many attempts  please refresh")
        except Exception as e:
            print("Error occured",e)
    return home

@start
def banking(user_name):
    x = Bank(user_name) 
    while True:
        print("""\n------------------\n'B' : Check Balance \n'D' : Deposit \n'W' : Withdraw \n'N' : Calculate Interest \n'T' : Transfer Money \n'V' : Transactions History \n'L' : Apply for loan \n'Q' : Logout And Return To Home Page\n------------------""")
        a = input("Select Option: ").upper()
        if a == 'B':
             x.balance()
        elif a == 'D':
            x.deposite()
        elif a == 'W':
            x.withdraw()
        elif a == 'Q':
            banking()
            break
        elif a == "N":
            y = Loans(user_name, x.get_balance())
            y.balance()
        elif a == 'T':
            x.transfer()
        elif a=="V":
            x.view_transactions()
        elif a=="L":
            x.apply_for_loan()
        else:
            print("Invalid input")

# Start the App
banking() 
