print("<------Welcome to the Quiz Game------>")

p = input("Do you want to play the Game? (yes/no): ").lower()

if p != 'yes':
    quit()

print("Okay! Let's play:")
score = 0

c = input("Do you want to start the quiz? (yes/no): ").lower()

while c == "yes":
    a = input("What does CPU stand for? ").lower()
    if a == "central processing unit":
        print("Well Done! Correct")
        score += 1
    else:
        print("Incorrect. The correct answer is 'Central Processing Unit'.")

    b = input("What does MOM stand for? ").lower()
    if b == "mother of motherboard":
        print("Well Done! Correct")
        score += 1
    else:
        print("Incorrect. (This is a fictional question for now.)")

    print(f"You got {score} points!")

    # Ask if they want to play again
    c = input("Do you want to play again? (yes/no): ").lower()

print(f"Thanks for playing! Your final score is {score}.")
