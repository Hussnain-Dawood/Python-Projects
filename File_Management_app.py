# file_write= open("sample.txt","w")
# file_write.write("Hello world !")
# file_write.close()

# file_read=open("sample.txt","r")

# content=file_read.read()

# print(content)
#file_read.close()
# #print(file_read.read())

import os

def create_file(filename):
    try:
        with open(filename , "x") as f: #just gives a short name (f) for the file, so you can use f.write(...), f.read(...), etc.
            print(f"{filename} is created successfully !")
    except FileExistsError:
        print(f"{filename} is already created !")
    except Exception as E:
        print("An error occur !")

def view_all_file():
    files=os.listdir() # give the list of all the dirextory
    if not  files:
        print("No files is present !")
    else:
        print("<----All Files ---->")
        for file in files:
            print("File name : ", file)
    
def delete_file(filename):
    try:
        os.remove(filename)
        print(f"{filename} is deleted successfully !")
    except FileExistsError:
        print("File is not present ")
    except Exception as E:
        print(" An error occur !")

def read_file(filename):
    try:
        with open(filename,"r") as f:
           content=f.read()
           print(f"Content of the {filename} ")
           print(content)
    except FileExistsError:
        print("File is not present ")
    except Exception as E:
        print(" An error occur !")

def write_file(filename):
    try:
        with open(filename,"w")as f:
            content=input("Write the Content you want to enter : \n")
            f.write(content)
            print(f"Content is added successfully  to the {filename}")
    except FileExistsError:
        print("File is not present ")
    except Exception as E:
        print(" An error occur !")

def edit_filename(filename):
    try:
        with open(filename ,"a") as f:
            content=input("Write the Content you want to enter : \n")
            f.write(content + "\n")
            print(f"Content is added successfully  to the {filename}")
    except FileExistsError:
        print("File is not present ")
    except Exception as E:
        print(" An error occur !")

def main ():
    while True:
         print("File Manager App")
         print("1: Create a File")
         print("2: Write a File")
         print("3: Delete a File")
         print("4: Read  a File")
         print("5: Edit a File")
         print("6: View all File")
         print("7: Exit")

         option=int(input("Enter the Option Number : "))

         if option ==1 :
             filename=input("Enter the File name : ").title()
             create_file(filename)
         elif option ==2:
             filename=input("Enter the File name : ").title()
             write_file(filename)
         elif option ==3:
             filename=input("Enter the File name : ").title()
             delete_file(filename)
         elif option ==4:
             filename=input("Enter the File name : ").title()
             read_file(filename)
         elif option ==5:
             filename=input("Enter the File name : ").title()
             edit_filename(filename)
         elif option ==6:
             view_all_file()
         elif option ==7:
             break
        



main()




