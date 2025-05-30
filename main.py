from atm import ATM
from data import accounts

def main():
    atm = ATM(accounts)
    atm.run()

if __name__ == "__main__":
    main()
