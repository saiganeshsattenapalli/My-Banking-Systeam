from fastapi import FastAPI, Request, Form,staticfiles,APIRouter,Depends, HTTPException
from fastapi.templating import Jinja2Templates
import secrets,string,sqlite3,uuid,pickle
import numpy as np, pandas as pd,matplotlib.pyplot as plt,warnings
from datetime import datetime
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
warnings.filterwarnings("ignore", message="X does not have valid feature names")


def cap(): #this function is for captcha generation
    captcha_chars = string.digits + string.ascii_letters
    return "".join(secrets.SystemRandom().choices(captcha_chars, k=6))

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", staticfiles.StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="SAi-ganesh-super-secret-bank-key-2426")
class Bank:
    def __init__(self, userid:str):
        self.userid = userid
        self.conn = sqlite3.connect("bank.db")
        self.cursor = self.conn.cursor()

    @staticmethod
    def transactionid(): #this function is for transactionid generation
        return str(uuid.uuid4())

    def edit_profile(self):
        try:
            self.cursor.execute("SELECT * FROM users")
            d=self.cursor.fetchall()
        except Exception as e:
            print("Error occured while editing the profile",e)

    def deposit_amount(self, amount:int):
        try:
            if amount < 1:
                return False, "Minimum deposit is ₹1."
        
            #updating the balance
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users SET balance = balance + ? WHERE userid = ?", (amount, self.userid))

            # Log this as a transaction in the database so it shows on the dashboard
            cursor.execute("SELECT username,account_number,balance FROM users WHERE userid = ?", (self.userid,))
            user_data = cursor.fetchone()
            user_name=user_data[0]
            sender_acc=user_data[1]
            balance=user_data[2]
        
            cursor.execute('''
            INSERT INTO transactions 
            (transactionid, sender_username, sender_acc, receiver_acc, receiver_username, amount, method, note, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (Bank.transactionid(), "Cash Deposit",0, sender_acc,user_name, amount, "DEPOSIT", "Self Deposit", "✅ Success"))
            self.conn.commit()
            # here the zero refferes to NULL valuse 

            return True, f"Deposited ₹{amount:.2f} successfully!. New balance: ₹{balance}"
        
        except Exception as e:
             # EMERGENCY BUTTON: If anything crashes, UNDO EVERYTHING
            self.conn.rollback()
            return False, f"System error. No money was deposited {str(e)}."
        
    
    def withdraw_amount(self, amount:int):
        try:
            if amount < 1:
                return False, "Minimum withdrawal is ₹1."

            # Execute the withdrawal
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users SET balance = balance - ? WHERE userid = ? AND balance >= ?",(amount,self.userid,amount))
            if cursor.rowcount==0:
                self.conn.rollback()
                return False, "Insufficient funds. Please check your balance."

            # Log this as a transaction in the database so it shows on the dashboard
            cursor.execute("SELECT username,account_number,balance FROM users WHERE userid = ?", (self.userid,))
            user_data = cursor.fetchone()
            user_name=user_data[0]
            sender_acc=user_data[1]
            balance=user_data[2]
        
            cursor.execute('''
            INSERT INTO transactions 
            (transactionid, sender_username, sender_acc, receiver_acc, receiver_username, amount, method, note, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (Bank.transactionid(), user_name, sender_acc, 0, "ATM Withdrawal", amount, "Withdrawal", "Self Withdrawal", "✅ Success"))
            self.conn.commit()
            # here the zero refferes to NULL valuse 

            return True, f"Successfully withdrew ₹{amount:.2f}. New balance: ₹{balance}"
        
        except Exception as e:
             # EMERGENCY BUTTON: If anything crashes, UNDO EVERYTHING
            self.conn.rollback()
            return False, f"System error. No money was withdrawed {str(e)}."
        
    def transfer(self,receiver_acc,amount,note,method):
        try:
            cursor = self.conn.cursor()
            if amount <= 0:
                return False, "Transfer amount must be greater than zero."

            cursor.execute("SELECT account_number, balance, username FROM users WHERE userid = ?", (self.userid,))
            sender_data = cursor.fetchone()
            sender_acc = sender_data[0]
            sender_balance = sender_data[1]
            sender_name = sender_data[2]

            if sender_acc == receiver_acc:
                return False, "You cannot transfer money to your own account."

            if amount >=sender_balance:
                cursor.execute("select username from users where account_number  = ?",(receiver_acc,))
                receiver_name = cursor.fetchone()
                if receiver_name:
                    receiver_name = receiver_name[0]
                else:                    
                    return False ,"Receiver account not found. Please verify the account number."
                cursor.execute('''
                    INSERT INTO transactions 
                    (transactionid, sender_username, sender_acc, receiver_acc, receiver_username, amount, method, note, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (Bank.transactionid(), sender_name, sender_acc, receiver_acc, receiver_name, amount, method, note, "Failed"))
                self.conn.commit()
                return False, "Insufficient funds. Please check your balance."
            
            cursor.execute("SELECT username FROM users WHERE account_number = ?", (receiver_acc,))
            receiver_data = cursor.fetchone()

            if not receiver_data:
                return False, "Receiver account not found. Please verify the account number."
            
            receiver_name = receiver_data[0]

            #EXECUTE THE TRANSFER SAFELY
            # 1. Deduct from SENDER
            cursor.execute("UPDATE users SET balance = balance - ? WHERE userid = ?", (amount, self.userid))
            
            # 2. Add to RECEIVER
            cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, receiver_acc))
            
            # 3. Create Receipt for transaction
            cursor.execute('''INSERT INTO transactions 
                           (transactionid,sender_username, sender_acc, receiver_acc, receiver_username, amount,method,note ,status) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
               (Bank.transactionid(),sender_name, sender_acc, receiver_acc, receiver_name, amount,method,note,"✅ Success"))
            # 4. SAVE EVERYTHING
            self.conn.commit()
            return True, f"Successfully transferred ₹{amount} to {receiver_name}."

        except Exception as e:
            # EMERGENCY BUTTON: If anything crashes, UNDO EVERYTHING
            self.conn.rollback()
            return False, f"System error. No money was transferred {str(e)}."

    def apply_for_loan(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE userid = ?",(self.userid,))
        # 1. GATHER DATA
        current_bal =0
        
        # Count user's transactions from DB
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE sender_id = ?", (self.userid,))
        txn_count = cursor.fetchone()[0]

        # 2. LOAD BRAIN
        try:
            with open('loan_model.pkl', 'rb') as f:
                model = pickle.load(f)
        except FileNotFoundError:
            return False, "failed to load Machine learning model"

        # 3. PREDICT
        features = np.array([[current_bal, txn_count]])
        prediction = model.predict(features)
        
        # 4. RESULT
        if prediction[0] == 1:
            return True,"success, ✅ CONGRATULATIONS! Loan Approved by AI."
        else:
            return False, "failed you can't get loan"

    def download_statement(self):
        print("\n--- 📥 DOWNLOADING STATEMENT ---")
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT account_number FROM users WHERE userid = ?",(self.userid,))
            test_acc=cursor.fetchone()
            query=f'''SELECT sender_id,sender_username,receiver_username,amount,transactionid,date,status FROM transactions WHERE sender_id= '{self.userid}' OR  receiver_acc= {test_acc[0]}'''
            df = pd.read_sql_query(query, self.conn)
            print(df.head())
            filename = f"{self.userid}_statement.csv"
            df.to_csv(filename, index=False)
            print("Statement ✅ succsessfully downloaded")
        except:
            print(f"Error occured while downloading the statement")
        
    
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
    def __init__(self, Username, Userid, Password,Balance1=0):
        self.Username = Username
        self.Userid=Userid
        self.Password = Password
        self.Balance1=Balance1
    @staticmethod
    def accountnum(): #this function is for account number generation
        return int("".join(secrets.SystemRandom().choices(string.digits,k=10)))
        
    def open_account(self):
        acc_num = Openaccount.accountnum()
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, userid, password, account_number,balance) VALUES (?, ?, ?, ?, ?)", 
                       (self.Username,self.Userid, self.Password, acc_num,self.Balance1))
            today_date = datetime.now().strftime("%B %d, %Y")
            conn.commit()
            return acc_num, today_date
        except sqlite3.IntegrityError:
            return sqlite3.IntegrityError()
        except Exception as e:
            return e
        finally:
            conn.close() 

# FAST API ROUTES 

# HOME ROUTE
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request,"home.html")

# Create account routes
@app.get("/create-account-form", response_class=HTMLResponse)
def create_account_form(request: Request):
    return templates.TemplateResponse(request,"create-ac-form.html")

@app.post("/create-account", response_class=HTMLResponse)
def create_account(request:Request,full_name:str=Form(...),user_id:str=Form(...),password:str=Form(...),confirm_password:str=Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse(request,"create-ac-form.html", {"error": "Passwords did not match."})
    
    new_user = Openaccount(full_name, user_id, password)
    new_user = new_user.open_account()

    if isinstance(new_user, sqlite3.IntegrityError):
        return templates.TemplateResponse(request,"create-ac-form.html", {"error": "User ID already exists."})
    elif isinstance(new_user, Exception):
        return templates.TemplateResponse(request,"create-ac-form.html", {"error": f"Error: {str(new_user)}"})
    else:   
        return templates.TemplateResponse(request,"account-success.html", {'full_name': full_name, 'user_id': user_id, 'account_number': new_user[0], 'creation_date': new_user[1]})


# Login form route
@app.get("/login-form", response_class=HTMLResponse)
def login_form(request: Request ): 
    return templates.TemplateResponse(request,"login-form.html", {"captcha": cap()})

# Login POST route (Strictly Authentication -> Redirect)
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, userid: str = Form(...), password: str = Form(...), real_captcha: str = Form(None), user_captcha: str = Form(...)):
    try:
        if real_captcha != user_captcha:
            new_captcha = cap()
            return templates.TemplateResponse(request,'login-form.html', {
                                        "captcha": new_captcha, 
                                        "error": "Security Verification Failed Due To Incorrect Captcha." })
        
        con = sqlite3.connect('bank.db')
        cursor = con.cursor()
        cursor.execute("SELECT userid FROM users WHERE userid = ? AND password = ?", (userid, password))
        user_data = cursor.fetchone()
        con.close()

        if not user_data:
            new_captcha = cap() 
            return templates.TemplateResponse(request,'login-form.html', {
                                            "captcha": new_captcha, 
                                            "error": "Invalid User ID or Password."})
        
        # Give the VIP wristband and redirect to Dashboard!
        request.session["user_id"] = userid 
        return RedirectResponse(url='/dashboard/', status_code=303)

    except Exception as e:
        return f"An internal server error occurred while logging in: {str(e)}"

# Logout route
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

    

# 1. THE BOUNCER: Checks the VIP wristband (cookie) authorization
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        # Kicks them to login if they aren't authenticated
        raise HTTPException(status_code=303, headers={"Location": "/login-form"})
    return user_id

# 2. THE SUB-PANEL: Create the secure zone
dashboard_router = APIRouter(
    prefix="/dashboard",
    dependencies=[Depends(get_current_user)]
)


#DASHBOARD ROUTE
@dashboard_router.get("/", response_class=HTMLResponse)
def dashboard(request: Request,user_id:str=Depends(get_current_user)):

    try:
        con = sqlite3.connect('bank.db')
        cursor = con.cursor()
        
        cursor.execute("SELECT username, balance, account_number FROM users WHERE userid = ?", (user_id,))
        user_data = cursor.fetchone()
        username, balance, account_number = user_data

        cursor.execute("SELECT * FROM transactions WHERE sender_acc= ? OR receiver_acc= ? ORDER BY date DESC", (account_number, account_number))
        raw_transactions = cursor.fetchall()
        con.close()

        formatted_transactions = []
        for row in raw_transactions:
            if row[3] == account_number:
                tx_type = "Sent" 
                counterparty = f"To: {row[5]}"
                sign = "-"
            else:
                tx_type = "Received"
                counterparty = f"From: {row[2]}"
                sign = "+"
            formatted_transactions.append({
                "transactionid": row[1],
                "type": tx_type,
                "counterparty": counterparty,
                "amount": f"{sign}₹{row[6]}",
                "note": row[9] if row[9] else "No note",
                "status": row[7],
                "date": row[8][:16],
                "method": row[10]
            })

        return templates.TemplateResponse(request,'homepage.html', {
            "user_name": username,
            "total_balance": balance,
            "transactions": formatted_transactions
        })
    except Exception as e:
        return f"Database error: {str(e)}"



# SECURED TRANSACTION ROUTES 

#Transfer money route
@dashboard_router.get("/transfer-money-form", response_class=HTMLResponse)
def transfer_money_form(request: Request):
    return templates.TemplateResponse(request,"transfer-money-form.html",)

@dashboard_router.post("/transfer-money", response_class=HTMLResponse)
def transfer_money(request: Request,user_id: str = Depends(get_current_user), receiver_acc: int = Form(...), amount: float = Form(...),note: str = Form(None), method: str = Form(...)):
    user_bank = Bank(user_id)
    success, message = user_bank.transfer(receiver_acc, amount, note, method)
    if not success:
        return templates.TemplateResponse(request,"transfer-money-form.html", {"error": message})
    return templates.TemplateResponse(request,"transfer-result.html", {"success": success, "message": message})

#Deposit money route
@dashboard_router.get("/deposit", response_class=HTMLResponse)
def deposit(request: Request):
    return templates.TemplateResponse(request,"deposite-money-form.html")

@dashboard_router.post("/deposite-money", response_class=HTMLResponse)
def deposite_money(request: Request, amount: float = Form(...),user_id: str = Depends(get_current_user)):
    user_bank = Bank(user_id)
    success, message = user_bank.deposit_amount(amount)
    if not success:
        return templates.TemplateResponse(request,"deposite-money-form.html", {"error": message})
    return templates.TemplateResponse(request,"deposite-result.html", {"success": success, "message": message})

#Withdraw money route
@dashboard_router.get("/withdraw-money-form", response_class=HTMLResponse)
def withdraw_money_form(request: Request):
    return templates.TemplateResponse(request,"withdraw-money-form.html")

@dashboard_router.post("/withdraw-money", response_class=HTMLResponse)
def withdraw_money(request: Request, user_id: str = Depends(get_current_user), amount: float = Form(...)):
    user_bank = Bank(user_id)
    success, message = user_bank.withdraw_amount(amount)
    if not success:
        return templates.TemplateResponse(request,"withdraw-money-form.html", {"error": message})
    return templates.TemplateResponse(request,"withdraw-result.html", {"success": success, "message": message})

#AI loan approval route
@dashboard_router.get("/apply-loan", response_class=HTMLResponse)
def apply_loan(request: Request,user_id:str=Depends(get_current_user)):
    user_bank = Bank(user_id)
    status,message=user_bank.apply_for_loan()
    return templates.TemplateResponse(request,"loan-form.html", {"status":status,"message":message})

@dashboard_router.get("/download-satatement-form")
def statement(request:Request,date_filter:str="hellooo"):
    return "hello"


# Plug the VIP section into the main app
app.include_router(dashboard_router)

# CONTACT US ROUTE
@app.get("/contact-form")
def contact_form(request:Request):
    return templates.TemplateResponse(request,"contact-form.html")

@app.post("/contact",response_class=HTMLResponse)
def contact(request:Request,name:str=Form(...), age:int=Form(None), email:str=Form(None), num:str=Form(None), info:str=Form(None)):
    ip=request.headers.get("User-Agent")
    print(name)
    return templates.TemplateResponse(request,"contact.html",{"name":name,"age":age, "email-id":email, "mobile-num":num, "issue":info,"ip":ip})
