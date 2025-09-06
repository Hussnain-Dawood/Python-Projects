# cv2 is open-cv library of the python
import cv2
a=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# Give access to the camera
b=cv2.VideoCapture(0)

while True:
    # c_rec means rectangle and d refer to the image 
    c_rec,d_imag=b.read()
    # Convert the image to gray scale
    e=cv2.cvtColor(d_imag,cv2.COLOR_BGR2GRAY)
    # Detect the face
    f=a.detectMultiScale(e,1.1,5)
# Draw the rectangle around the face
    for(x1,y1,w1,h1)in f:
     cv2.rectangle(d_imag,(x1,y1),(x1+w1,y1+h1),(255,0,0),5)
# Show the image
     cv2.imshow('img',d_imag)
# Wait for the key to be pressed
    h=cv2.waitKey(40) & 0xff

    if h==40:
       break       
b.release()
cv2.destroyAllWindows()