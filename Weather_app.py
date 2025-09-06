import requests
import pyttsx3

#Make dictionary of city and its code 
import json
while True:
    city = input("<------Enter city name------>\n")
    url = f"https://api.weatherapi.com/v1/current.json?key=9636fb068ffb4b4aa9c94316250903&q={city}"  # Fixed format

    r = requests.get(url)
    weather_dictionary=json.loads(r.text)
    city_name = weather_dictionary['location']['name']
    temperature = weather_dictionary['current']['temp_c']
    
    print(f"City Name : {city_name}")
    print(f"Temperature: {temperature}°C")

    engine = pyttsx3.init()
    engine.say(f"City Name: {city_name}, Temperature: {temperature} degree Celsius")

    engine.runAndWait()
    a=input("Do you want to continue? (y/n): ")
    if a.lower() == "n":
        break
