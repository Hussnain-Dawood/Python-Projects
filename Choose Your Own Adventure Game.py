name=input("Type your name:")
print(f"<-----Welcome  {name} to this Adventure Game !----->")

answer=input("You are a dirt road ,  it has come to an end and you can go to the left or right ! \n which way you want to go  ? ").lower()

if answer=="left":
    answer=input("You come to the river , you can walk around it or swim accross ! \n Type walk/swim ? ").lower()
    if answer=="walk":
        print("The River is left behind !")
        print(f"You Lose !  {name}")
    elif answer=="swim":
        print("The River is Filled with monster !")
        print(f"You Lose !  {name}")
elif answer=="right":
    answer=input("You come to a bridge , you can cross it or go back to the village and try again ! \n Type cross/village ? ").lower()
    if answer=="cross":
        print("Bridge doesnt break your weight !")
        print(f"You Lose !  {name}")
    elif answer=="village":
        print("Smart Choice Sometimes it is best to think before act !")
        print(f"You're Awesome {name}")
else:
    print(f"You Lose !  {name}")