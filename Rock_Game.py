import random

list_items = ["Rock", "Paper", "Scissor"]
print("<-----Welcome to the Rock Paper Scissor Game------->")
# Title captialize the letter
while True:
    user_option = input("Enter your Move (Rock, Paper, Scissor): ").title()
    computer_option = random.choice(list_items)

    print(f"Player Choice = {user_option} , Bot Choice = {computer_option}")

    if user_option == computer_option:
        print("The Match is Draw")
    elif user_option == "Rock" and computer_option == "Paper":
        print("Bot has won the match")
    elif user_option == "Rock" and computer_option == "Scissor":
        print("Player has won the match")
    elif user_option == "Paper" and computer_option == "Rock":
        print("Player has won the match")
    elif user_option == "Paper" and computer_option == "Scissor":
        print("Bot has won the match")
    elif user_option == "Scissor" and computer_option == "Rock":
        print("Bot has won the match")
    elif user_option == "Scissor" and computer_option == "Paper":
        print("Player has won the match")
    else:
        print("Invalid choice! Please enter Rock, Paper, or Scissor.")

    ask = input("Do you want to play again? (yes/no): ").lower()
    if ask != "yes":
        print("Thanks for playing! Goodbye.")
        break
