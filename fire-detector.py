'''
Created by: Fuat Yiğit Koçyiğit, Zülal Karın, Ayca Tanışlı
Date: 30/05/2023
Description: This program detects fire in a video file or a webcam stream.

This project is prepared for CMPE326 - Multimedia Course at TED University and will also
be presented at the 2023 GBYF (Genç Beyinler Yeni Fikirler) in Ankara, Turkey.
'''

import cv2
import numpy as np
import smtplib
import playsound
import threading

# Flag variables to monitor the status of alarm and email
Alarm_Status = False
Email_Status = False
Fire_Reported = 0

# This function will play alarm sound
def play_alarm_sound_function():
    while True:
        playsound.playsound('alarm-sound.mp3', True)

# This function will send an email alert
def send_mail_function():
    recipientEmail = "Enter_Recipient_Email"
    recipientEmail = recipientEmail.lower()

    try:
        # Set up a server for sending an email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("Enter_Your_Email (System Email)", 'Enter_Your_Email_Password (System Email')
        server.sendmail('Enter_Your_Email (System Email)', recipientEmail, "Warning A Fire Accident has been reported on ABC Company")
        print("sent to {}".format(recipientEmail))
        server.close()
    except Exception as e:
        print(e)

# Use either webcam or a video file for input
# video = cv2.VideoCapture(0)
video = cv2.VideoCapture("Fire_Video.mp4")
video2 = cv2.VideoCapture("Fire_Video.mp4")

while True:
    # Read frames from both video sources
    grabbed1, frame1 = video.read()
    grabbed2, frame2 = video2.read()

    if not grabbed1 or not grabbed2:
        break

    # Resize the frames to a manageable size
    frame1 = cv2.resize(frame1, (960, 540))
    frame2 = cv2.resize(frame2, (960, 540))

    # Apply gaussian blur to frame2
    blur = cv2.GaussianBlur(frame2, (21, 21), 0)
    # Convert the frame2 color space from BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Define the color range for detecting fire
    lower = [18, 50, 50]
    upper = [35, 255, 255]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    # Create a mask for fire detection
    mask = cv2.inRange(hsv, lower, upper)
    # Apply mask to the frame
    output = cv2.bitwise_and(frame2, hsv, mask=mask)

    # Count the number of red pixels in the image
    no_red = cv2.countNonZero(mask)

    # If the number of red pixels is above a certain threshold, fire is detected
    if int(no_red) > 15000:
        Fire_Reported = Fire_Reported + 1
        print("Fire Detected!")

    # Concatenate frames horizontally
    combined_frame = np.vstack((output, frame1))

    # Display the combined frame
    cv2.imshow("Combined Frame", combined_frame)

    # If fire is reported, start the alarm and send an email
    if Fire_Reported >= 1:
        if not Alarm_Status:
            threading.Thread(target=play_alarm_sound_function).start()
            Alarm_Status = True

        if not Email_Status:
            threading.Thread(target=send_mail_function).start()
            Email_Status = True

    # If 'q' is pressed on the keyboard, stop the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close all OpenCV windows and release the video sources when done
cv2.destroyAllWindows()
video.release()
video2.release()
