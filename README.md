Overview:
This is a professional Python-based banking application developed to demonstrate core
software engineering and security principles. It features a robust authentication layer and
a functional ATM interface.
Key Technical Features:
Security Decorators: Implemented a custom @start decorator to handle user authentication and session security before accessing banking functions.
Weighted CAPTCHA: Features a dynamic 6-character security code generator using random.choices with specific probability weights for Uppercase (50%), Lowercase (20%), and Digits (30%).
Object-Oriented Programming (OOP): Manages financial state (balance, deposits, and withdrawals) through a clean bank class.
ˆntelligent Lockout: Integrated logic to track failed login attempts, automatically denying access after multiple incorrect tries to prevent brute-force attacks
How to Run:
1.Clone this repository to your local machine (e.g., your MacBook M4).
2.Run the script using Python:
python3 mybank.py
3.Log in using the default credentials:
Username: saiganesh
Password: 2426
Skills Demonstrated:
ython Standard Library (random, string)
Decorator Design Pattern
Encapsulation and Class Logic
Input Validation and Error Handling
