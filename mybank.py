import random as ran
import string
def cap(): #this function is used to generate captcha
    a=list(string.digits)
    c=list(string.ascii_lowercase)
    d=list(string.ascii_uppercase)
    cd=a+c+d
    w=[50]*len(d)
    w1=[20]*len(c)
    w2=[30]*len(a)
    w=w+w1+w2
    m="".join(ran.choices(cd,weights=w,k=6))
    return m
class bank:
        def __init__(self,deposite=0,withdraw=0):
            self.balance=0
            self.d=deposite
            self.w=withdraw
        def Balance(self):
            c=0
            print(f"Your current balance is {self.balance}")
        def deposite(self):
            d=int(input("how much would you like to deposite:"))
            if d<=0:
                print("Minimum deposite is 1")
            else:
                self.balance+=d
                print(f"Your current balance is {self.balance}")
        def withdraw(self):
            w=int(input("how much would you like to withdraw:"))
            if w<=0:
                print("Mimnimum withdraw is 1")
            elif w>self.balance:
                print("Infulent balance")
            else:
                self.balance-=w 
                print(f"Your current balance is {self.balance}")
username=input("Enter username:")
password=input("Enetr password:")
def start(b):#the b is the original banking function
   def login():#this is the wrapper function to login before entering into bank
        attempts = 0
        global username,password
        while True:
            if username == "saiganesh":
                if password == "2429":
                    m = cap()
                    print(f"captcha is {m}")
                    c=input("Enter captcha:")
                    if c==m:
                         print("welcome to saiganesh Bank")
                         b()
                         break
                    else:
                        m=cap()
                        print(f"captcha is {m}")
                        c=input(" captcha is incorrect Again Enter captcha:")
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
def banking():
    x=bank()
    while True:
        print("""checking balance enter \'B\' \nFor deposite enter \'D\' \nFor withdraw enter \'W\' \nFor logout enter \'Q\'""")
        a=input().upper()
        if a=='B':
             x.Balance()
        elif a=='D':
            x.deposite()
        elif a=='W':
            x.withdraw()
        elif a=='Q':
            print("You are sucessfully logout see you soon")
            break
        else:
            print("Invalid input")
banking()
