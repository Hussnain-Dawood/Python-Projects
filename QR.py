#pip install qrcode this is the library
#pip install pillow this is used to show the qr code on the screen

import qrcode

IBAN=input("Enter your Bank account number = ")

#https://pay?pa=IBAN&pn=Name(Hussnain)&am=Amount(1000)&cu=currency&tn=Message

#Define the Payment URL based upon the app

Local_Bank = f'https://pay?pa={IBAN}&pn=Recipient%20Name%Local&mc=1234'
Bank = f'https://pay?pa={IBAN}&pn=Recipient%20Name&mc=1234'

#Create QR code for each url using QR make function

Local_Bank_qr=qrcode.make(Local_Bank)
Bank_qr=qrcode.make(Bank)

#Save the QR code to the image 

# Local_Bank_qr.save("local_bank.png")
# Bank_qr.save("bank.png")

# Display the qr code using pillow

Local_Bank_qr.show()
Bank_qr.show()
