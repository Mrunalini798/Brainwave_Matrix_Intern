class ATM:
    def __init__(self, accounts):
        self.accounts = accounts
        self.current_account = None

    def login(self):
        account_number = input("Enter account number: ")
        pin = input("Enter PIN: ")
        account = self.accounts.get(account_number)

        if account and account.check_pin(pin):
            print("Login successful!")
            self.current_account = account
            return True
        print("Invalid credentials.")
        return False

    def run(self):
        if not self.login():
            return

        while True:
            print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. Change PIN\n5. Exit")
            choice = input("Select option: ")

            if choice == "1":
                print(f"Balance: ${self.current_account.balance}")
            elif choice == "2":
                amount = float(input("Enter amount to deposit: "))
                self.current_account.deposit(amount)
                print("Deposit successful.")
            elif choice == "3":
                amount = float(input("Enter amount to withdraw: "))
                if self.current_account.withdraw(amount):
                    print("Withdrawal successful.")
                else:
                    print("Insufficient funds.")
            elif choice == "4":
                old_pin = input("Enter current PIN: ")
                new_pin = input("Enter new PIN: ")
                if self.current_account.change_pin(old_pin, new_pin):
                    print("PIN changed successfully.")
                else:
                    print("Incorrect current PIN.")
            elif choice == "5":
                print("Thank you for using the ATM.")
                break
            else:
                print("Invalid option.")
