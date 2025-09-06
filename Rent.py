print("<---Rent Calculator--->")
list_item = {}
total = 0

while True:
    a = input("Enter the item of the Budget (or type 'done' to finish):\n").title()
    if a.lower() == "done":
        break

    try:
        b = int(input("Enter the amount of the item:\n"))
    except ValueError:
        print("Please enter a valid number for the amount.")
        continue

    list_item[a] = b
    total += b

print("\n<---Budget Summary--->")
for item, amount in list_item.items():
    print(f"{item}: Rs {amount}")

print(f"\nTotal Budget: Rs {total}")
