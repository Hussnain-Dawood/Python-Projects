# Write a Python program to create a class that represents a shape. Include
# methods to calculate its area and perimeter. Implement subclasses for 
# different shapes like circle, triangle, and square.

class Shape():
    def __init__(self):
        self.a=0
        self.b=0
        self.c=0
        self.d=0

    def getdata(self):
        self.a=input("Enter the value of the first side :")
        self.b=input("Enter the value of the Second  side :")
        self.c=input("Enter the value of the Third side :")
        self.d=input("Enter the value of the Fourth side :")

    def shapeteller(self):
        if(self.a == self.b and self.a==self.c and self.a==self.d  and self.b==self.a and  self.b==self.c and self.b==self.d and self.c==self.a and self.c==self.b and self.c==self.d and self.d==self.a and self.d==self.b and self.d==self.c ):
            print("This is Square Shape")
        elif(self.a == self.b and self.a==self.c   and self.b==self.a and  self.b==self.c and self.c==self.a and self.c==self.b ):
            print("This is Triangle Shape ")
        else:
            print("This is Circle Shape")
s=Shape()
s.getdata()
s.shapeteller()