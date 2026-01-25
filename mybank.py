import random as ran
import string
import sqlite3 # 1. IMPORT SQL

# --- DATABASE SETUP ---
def setup_db():
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, balance INTEGER)")
    
    # Check if 'saiganesh' exists, if not, create him with 0 balance
    cursor.execute("SELECT * FROM users WHERE username = 'saiganesh'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, balance) VALUES ('saiganesh', 0)")
        conn.commit()
    
    conn.close()

# Run setup immediately
setup_db()

def cap(): 
    cd = list(string.digits + string.ascii_letters)
    w = list(([30]*10) + ([20]*26) + ([50]*26))
    m = "".join(ran.choices(cd, weights=w, k=6))
    return m

class bank:
    def __init__(self, username):
        self.username = username
        self.conn = sqlite3.connect("bank.db") # Connect to DB
        self.cursor = self.conn.cursor()
        
        # FETCH EXISTING BALANCE FROM DB
        self.cursor.execute("SELECT balance FROM users WHERE username = ?", (self.username,))
        data = self.cursor.fetchone()
        if data:
            self.__balance = data[0]
        else:
            self.__balance = 0

    def save_to_db(self):
        # UPDATE SQL QUERY
        self.cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (self.__balance, self.username))
        self.conn.commit() # Save changes

    def balance(self):
        # Refresh balance from DB just in case
        self.cursor.execute("SELECT balance FROM users WHERE username = ?", (self.username,))
        self.__balance = self.cursor.fetchone()[0]
        print(f"Your current balance is {self.__balance}")

    def deposite(self):
        try:
            d = int(input("how much would you like to deposite: "))
            if d <= 0:
                print("Minimum deposite is 1")
            else:
                self.__balance += d
                self.save_to_db() # SAVE TO SQL
                print(f"Your current balance is {self.__balance}")
        except ValueError:
            print("Invalid input Enter a number")

    def withdraw(self):
        try:
            w = int(input("how much would you like to withdraw: "))
            if w <= 0:
                print("Mimnimum withdraw is 1")
            elif w > self.__balance:
                print("Insufficient balance")
            else:
                self.__balance -= w
                self.save_to_db() # SAVE TO SQL
                print(f"Your current balance is {self.__balance}")
        except ValueError:
            print("Invalid input Enter a number")

    def get_balance(self):
        return self.__balance 

    # Close connection when object is destroyed (Optional but good practice)
    def __del__(self):
        self.conn.close()

class savingsaccount(bank):
    def __init__(self, username, balance1=0):
        # We need to initialize the parent with username
        super().__init__(username)
        # In this logic, we use the balance passed or fetch from parent
        self.balance1 = balance1
        self.interest_rate = 0.05

    def balance(self):
        interest1 = self.interest_rate * self.balance1
        total = interest1 + self.balance1
        print(f"The total amount after adding interest: {total}")
        
def start(b):
   def login():
        attempts = 0
        username_input = input("Enter username: ")
        password = input("Enter password: ")
        while True:
            # NOTE: Ideally, we should check password from SQL too, 
            # but I kept your logic for now to keep it simple.
            if username_input == "saiganesh":
                if password == "2429":
                    m = cap()
                    print(f"The captcha: {m}")
                    c = input("Enter captcha: ")
                    while True:
                        if c == m:
                            print("welcome to saiganesh Bank")
                            # Pass the username to the banking function
                            b(username_input) 
                            return
                        else:
                            m = cap()
                            print(f"The new captcha: {m}")
                            c = input("captcha is incorrect Again Enter the captcha: ")
                else:
                    if attempts > 8:
                        print("Too many incorrect attempts. Access denied.")
                        break
                    else:
                        attempts += 1
                        password = input("Incorrect password enter again: ")
            else:
                if attempts > 4:
                    print("Too many incorrect attempts. Access denied.")
                    break
                else:
                   attempts += 1
                   username_input = input("Incorrect username enter again: ")
   return login

@start
def banking(user_name): # Takes username as argument
    x = bank(user_name) # Sends username to Bank Class
    while True:
        print("""\nChecking balance enter 'B' \nFor deposite enter 'D' \nFor withdraw enter 'W' \nFor interest calculation 'N' \nFor logout enter 'Q'""")
        a = input().upper()
        if a == 'B':
             x.balance()
        elif a == 'D':
            x.deposite()
        elif a == 'W':
            x.withdraw()
        elif a == 'Q':
            print("You are sucessfully logout see you soon")
            break
        elif a == "N":
            # Pass username to savings account too
            y = savingsaccount(user_name, x.get_balance())
            y.balance()
        else:
            print("Invalid input")

banking()
