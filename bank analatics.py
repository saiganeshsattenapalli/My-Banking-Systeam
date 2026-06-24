import sqlite3 
def view_all_users():
    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
    
        # Get all data
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        
        print(f"\n{'USERNAME':<30} | {'User ID':<20} | {'PASSWORD':<12} | {'ACCOUNT NO':<12} | {'BALANCE'} | {'CIBIL SCORE'}")
        print("=" * 120)
    
        if not rows:
            print("📭 Database is empty.")
        else:
            for row in rows:
                if row[6]==-1:
                    cibil="no creadit history"
                else:
                    cibil=row[6]
                print(f"{row[0]:<30} | {row[1]:<20} | {row[2]:<12} | {row[3]} | ₹{row[4]} | {cibil} ")
        conn.close()
    except sqlite3.OperationalError:
        print("data not found")
view_all_users()