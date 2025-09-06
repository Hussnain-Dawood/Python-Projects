from instagrapi import Client

# Create client
cl = Client()

print("<---- Welcome to the Instagram Bot ----->")
u_name = input("Enter your Instagram username: ")
p_word = input("Enter your Instagram password: ")

# Login
cl.login(u_name, p_word)

while True:
    print("\nMenu:")
    print("1: Follow a user")
    print("2: Upload a picture")
    print("3: Unfollow a user")
    print("4: Send a message")
    print("5: Get user information")
    print("6: Exit the Bot")

    try:
        choice = int(input("Enter the Option Number: "))
    except ValueError:
        print("Invalid input, please enter a number.")
        continue

    if choice == 1:
        f_user = input("Enter the username you want to follow: ")
        user_id = cl.user_id_from_username(f_user)
        cl.user_follow(user_id)
        print(f"Followed {f_user}")

    elif choice == 2:
        file_path = input("Enter the file path of the picture you want to upload: ")
        caption = input("Enter caption for the picture: ")
        cl.photo_upload(file_path, caption)
        print("Photo uploaded successfully!")

    elif choice == 3:
        f_user = input("Enter the username you want to unfollow: ")
        user_id = cl.user_id_from_username(f_user)
        cl.user_unfollow(user_id)
        print(f"Unfollowed {f_user}")

    elif choice == 4:
        send_message = input("Enter the message you want to send: ")
        num = int(input("How many users do you want to send the message to? "))
        users = []
        for i in range(num):
            u = input(f"Enter username {i+1}: ")
            users.append(cl.user_id_from_username(u))
        cl.direct_send(send_message, users)
        print("Message sent!")

    elif choice == 5:
        f_user = input("Enter the username to get information: ")
        user_id = cl.user_id_from_username(f_user)
        info = cl.user_info(user_id).dict()
        print("\nUser Information:")
        for k, v in info.items():
            print(f"{k}: {v}")

    elif choice == 6:
        print("Thanks for using the Instagram Bot!")
        break

    else:
        print("Invalid choice! Please try again.")
