import pyttsx3

engine = pyttsx3.init()
print("<-----Welcome to the Robo Speaker------>")

while True:
    text = input("Enter the text you want to speak: ")
    if text.lower() == "exit":
        break
    engine.say(text)
    engine.runAndWait()