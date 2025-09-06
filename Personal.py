#  Write a Python program to create a person class. Include attributes 
# like name, country and date of birth. Implement a method to determine 
# the person's age

class Personal():
    def __init__(self):
        self.name=0
        self.country=0
        self.dob=0

    def getdata(self):
        self.name=input("Enter your Name :")
        self.dob=input("Enter your date of Birth :")
        self.country=input("Enter your Country :")

    def show_data(self):
        print("Your Name is :", self.name)
        print("Your Date of Birth is :", self.dob)
        print("Your Country is :", self.country)

class person(Personal):
    def __init__(self):
        self.age=0

    def getdata(self):
     super().getdata()
     self.age=input("Enter your age ")
        
    def show_data(self):
        super().show_data()
        print("Your age is :",self.age)

        
p=person()
p.getdata()
p.show_data()


