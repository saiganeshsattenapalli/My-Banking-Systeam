import sqlite3
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
            sender_acc INTEGER ,
            receiver_acc INTEGER ,
            receiver_username TEXT,
            amount REAL,
            status TEXT DEFAULT 'failed',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note TEXT DEFAULT 'NULL',
            method TEXT DEFAULT 'online banking'
        )
    ''')

    conn.commit()
    conn.close()

# setup_database() # CALLING THE FUNCTION TO SETUP DATABASE
# conn = sqlite3.connect('bank.db')
# cursor = conn.cursor()
# cursor.execute("select * from users inner join transactions on userid=sender_id or account_number= receiver_acc")
# a=cursor.fetchall()
# df=pd.DataFrame(a)
# df2=df.to_html(index=False,header=False)
# # print(df2)
# app=fastapi.FastAPI()
# @app.get("/",response_class=fastapi.responses.HTMLResponse)
# def sai():
#       return df2
