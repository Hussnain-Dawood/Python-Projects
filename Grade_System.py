student = {}
choice = ""

def add_student(name, grade):
    if name in student:
        print(f"{name} already exists. Use update option instead.")
    else:
        student[name] = grade
        print(f"{name} is added with grade {grade}.")

def delete_student(name):
    if name in student:
        del student[name]
        print(f"{name} has been deleted from the system.")
    else:
        print("Name not found, try again!")

def update_student(name, grade):
    if name in student:
        student[name] = grade
        print(f"Grade updated: {name} now has grade {grade}.")
    else:
        print("Name not found, try again!")

def print_data():
    if not student:
        print("No student data available.")
    else:
        print("\n--- Student Records ---")
        for name, grade in student.items():
            print(f"Name: {name}, Grade: {grade}")
        print("------------------------\n")

while True:
    print("\n<--- Welcome to the Grade System ----->")
    print("<---- Main Menu --->")
    print("1: Add Student")
    print("2: Update Student")
    print("3: Delete Student")
    print("4: View All Students\n")

    try:
        option = int(input("Enter option number: "))
    except ValueError:
        print("Invalid input! Please enter a number.")
        continue

    if option == 1:
        name = input("Enter the name: ").title()
        try:
            grade = int(input("Enter the grade (number): "))
            add_student(name, grade)
        except ValueError:
            print("Invalid grade! Must be a number.")
    elif option == 2:
        name = input("Enter the name: ").title()
        try:
            grade = int(input("Enter the new grade: "))
            update_student(name, grade)
        except ValueError:
            print("Invalid grade! Must be a number.")
    elif option == 3:
        name = input("Enter the name: ").title()
        delete_student(name)
    elif option == 4:
        print_data()
    else:
        print("Invalid option! Try again.")

    choice = input("Do you want to perform another function? (Yes/No): ").strip().lower()
    if choice != "yes":
        print("Thanks a lot for using my program!")
        break
