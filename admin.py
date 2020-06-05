#from settings import *
from log import *
import tigris


if __name__ == "__main__":
    bank = tigris.TigrisBank()
    while True:
        cmd = int(input("1) new_account ; 2) send ; 3) balance, ; 4) all_balance ; 5) history\n"))

        if cmd == 1:
            user_id = input("user_id: ")
            balance = input("balance: ")
            bank.new_account(user_id, balance)
        elif cmd == 2:
            from_id = input("from_id: ")
            #from_id = 260861701279318019
            to_id = input("to_id: ")
            amount = input("amount: ")
            message = input("message: ")
            #message = "Init"
            bank.send(int(from_id), int(to_id), int(amount), message)
        elif cmd == 3:
            user_id = input("user_id: ")
            print(bank.get_balance(user_id))
        elif cmd == 4:
            bank.get_all_balance()
        elif cmd == 5:
            user_id = input("user_id: ")
            print(bank.get_history(user_id))
        print()

