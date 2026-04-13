def main_menu():
    print("Welcome to the Library Management System")
    print("1. View Books")
    print("2. Manage Members")
    print("3. Manage Transactions")
    print("4. Exit")
    choice = input("Please select an option: ")
    return choice

if __name__ == '__main__':
    while True:
        choice = main_menu()
        if choice == '4':
            break
        # Implement further functionalities here.
