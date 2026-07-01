# import asyncio
import psycopg as sql # Note: This is Psycopg 3, which supports native async
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

async def setup_database_async():
    # Establish an asynchronous connection
    con = await sql.AsyncConnection.connect(dbname=os.getenv("db_name"),user=os.getenv("db_user"),host=os.getenv("db_host"),port=os.getenv("db_port"),autocommit=True)
    
    # Create an async cursor
    async with con.cursor() as cursor:
        # Users Table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL,
                userid TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance NUMERIC(15, 2) DEFAULT 0.00,
                date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                cibil_score INTEGER DEFAULT -1
            )
        ''')
        
        # Transactions Table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                transactionid TEXT NOT NULL UNIQUE,
                sender_username TEXT NOT NULL,
                sender_acc TEXT NOT NULL,
                receiver_acc TEXT NOT NULL,
                receiver_username TEXT NOT NULL,
                amount NUMERIC(15, 2) NOT NULL,
                status TEXT DEFAULT 'failed',
                date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                note TEXT DEFAULT 'NULL',
                method TEXT DEFAULT 'internal_transfer'
            )
        ''')
        
    await con.close()

# To trigger it initially from your main startup script:
# asyncio.run(setup_database_async())
# with sql.connect(dbname="mybankdb",user="saiganeshsattenapalli",host="localhost",port="5432") as con:
#     with con.cursor() as cursor:
#         cursor.execute("select * from users")
#         a=cursor.fetchall()
#         print(a)


# def download_statement():
#         # try:
#             with sql.connect(dbname="mybankdb",user="saiganeshsattenapalli",host="localhost",port="5432") as con:
#                 with con.cursor() as cursor:
#                     cursor.execute("SELECT account_number FROM users WHERE userid = %s",("saiganesh",))
#                     test_acc=cursor.fetchone()
#                     query=f'''SELECT * FROM transactions WHERE sender_acc= %s OR  receiver_acc= %s'''
#                     df = pd.read_sql_query(query, con,params=(test_acc[0],test_acc[0]))
#                     print(df["date"]);print("start")
#                     print(df[df["date"]<datetime.datetime.now()]["date"]);print("stop")
#                     c=datetime.datetime.now()
#                     print(c)
#                     return "Statement ✅ succsessfully downloaded"
#         # except:
#         #     return f"Error occured while downloading the statement"
# print(download_statement())
