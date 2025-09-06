"""
twilio
datetime format
time
"""
"""
1:twilio client setup
2: user input
3: scheduling logic
4: send message using twilio api
"""

from twilio.rest import Client
from datetime import datetime, timedelta
import time

#1: Twilio SETUP

account_sid='AC0bf28e51af327afb45d3c53d8ca63262'
account_token='e11a4e3c6b3b4d36492a465c61b699c3'

client=Client(account_sid,account_token)

def send_message(receipent_number,message_body):
    try:
        message=client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=f'whatsapp:{receipent_number}'
        )
        print("Message sent successfully !")
    except Exception as e:
        print('An error occur !')

name=input("Enter you receipent  name : ")
recipent_number=input("Enter you whatsapp number with country code : ")
message_body=input("Enter your message : ")


date_str=input("Enter the date to send the message (YYYY-MM-DD): ")
time_str=input("Enter the time to send the message (HH:MM) in 24 format :")


schedule_datetime=datetime.strptime(f'{date_str}{time_str}',"%H-%M-%d %H:%M") #It takes a date/time string and a format string, and then converts (parses) it into a Python datetime object.
"""
from datetime import datetime

# a date in string form
date_str = "2025-08-21 15:45"

# strptime parses the string according to the format you give
dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

print(dt)

"""
current_time=datetime.now()

time_difference=schedule_datetime-current_time

delay_second=time_difference.total_seconds # convert time into second

if delay_second <=0:
    print("Time had passed !")
else:
    print(f"Messaage has delivered to the {name} at {schedule_datetime}")

    #wait until the schedule time
    time.sleep(delay_second)#1000
    send_message(recipent_number,message_body)

