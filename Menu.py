menu = {
    "Pizza": 40,
    "Burger": 200,
    "Salad": 70,
    "Coffe": 80
}

print("         <---Welcome to the Food Gala---->\n")
print("<--Here is our Menu -->\n")

for item, price in menu.items():
    print(f"{item}: Rs {price}")

order_total = 0

while True:
    item = input("\nEnter the item you want to order (or type 'done' to finish): ").title()
    
    if item.lower() == "done":
        break
    elif item in menu:
        order_total += menu[item]
        print(f"{item} added to your order.\n Current total: Rs {order_total}")
    else:
        print("Sorry, that item is not on the menu. Please try again.")

print(f"\nYour final bill is: Rs {order_total}")
print("Thank you for visiting the Food Gala!")
