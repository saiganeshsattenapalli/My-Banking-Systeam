import random as ran
import string
def cap(): #this function is used to generate captcha
    cd=list(string.digits+string.ascii_letters)
    w=list(([30]*10)+([20]*26)+([50]*26))
    m="".join(ran.choices(cd,weights=w,k=6))
    return m
class bank:#this the bank class 
        def __init__(self,balance=0):
            self.__balance=balance
        def balance(self):
            print(f"Your current balance is {self.__balance}")
        def deposite(self):
            d=int(input("how much would you like to deposite:"))
            if d<=0:
                print("Minimum deposite is 1")
            else:
                self.__balance+=d
                print(f"Your current balance is {self.__balance}")
        def withdraw(self):
            w=int(input("how much would you like to withdraw:"))
            if w<=0:
                print("Mimnimum withdraw is 1")
            elif w>self.__balance:
                print("Infulent balance")
            else:
                self.__balance-=w
                print(f"Your current balance is {self.__balance}")
        def get_balance(self):#this function is used as argument for savingsaccount
            return self.__balance 
# 'SavingsAccount' inherits from 'bank'
class SavingsAccount(bank):
    def __init__(self,balance1=0):
        super().__init__(balance1)#this line inherits from bank class
        self.balance1=balance1
        self.interest_rate = 0.05
    def balance(self):
        interest1=self.interest_rate * self.balance1
        interest1=interest1+self.balance1
        # It can access its own balance (if it wasn't private)
        print(f"the total rate after adding interest {interest1}")
def start(b):#the b is the original banking function
   def login():#this is the wrapper function to login before entering into bank
        attempts = 0
        username=input("Enter username:")
        password=input("Enetr password:")
        while True:
            if username == "saiganesh":
                if password == "2429":
                    m = cap()
                    print(f"The captcha: {m}")
                    c=input("Enter captcha: ")
                    while True:
                        if c==m:
                            print("welcome to saiganesh Bank")
                            b()
                            return
                        else:
                            m=cap()
                            print(f"The new captcha: {m}")
                            c=input("captcha is incorrect Again Enter the captcha:")
                else:
                    if attempts>8:
                        print("Too many incorrect attempts. Access denied.")
                        break
                    else:
                        attempts+=1
                        password=input("Inncorrect password enter again:")
            else:
                if attempts>4:
                    print("Too many incorrect attempts. Access denied.")
                    break
                else:
                   attempts+=1
                   username=input("Inncorrect username enter again:")
   return login
@start
def banking():#this is the main function and the actuall intraface of bank
    x=bank()
    while True:
        print("""checking balance enter \'B\' \nFor deposite enter \'D\' \nFor withdraw enter \'W\' \nfor interest calculation \'N\' \nFor logout enter \'Q\'""")
        a=input().upper()
        if a=='B':
             x.balance()
        elif a=='D':
            x.deposite()
        elif a=='W':
            x.withdraw()
        elif a=='Q':
            print("You are sucessfully logout see you soon")
            break
        elif a=="N":
            y=SavingsAccount(x.get_balance())
            y.balance()
        else:
            print("Ivalid input")

banking()
