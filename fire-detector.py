'''
Created by: Fuat Yiğit Koçyiğit, Zülal Karın, Ayca Tanışlı
Date: 30/05/2023
Description: This program detects fire in a video file or a webcam stream.

This project is prepared for CMPE326 - Multimedia Course at TED University and will also
be presented at the 2023 GBYF (Genç Beyinler Yeni Fikirler) in Ankara, Turkey.
'''
import os
import threading
import cv2
import numpy as np
import smtplib
import playsound
import time
import pygame as pygame
from twilio.rest import Client
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Flag variables to monitor the status of alarm and email
Alarm_Status = False
Email_Status = False
Wp_Status = False
Fire_Reported = 0
sensitivity_level = 15000
start_time = 0
configuration_completed = False

# This function will play alarm sound
def play_alarm_sound_function():
    #play the alarm sound 1 time
    pygame.mixer.init()
    pygame.mixer.music.load("alarm-sound.mp3")
    pygame.mixer.music.play()

    #playsound.playsound('alarm-sound.mp3', True)

# This function will send an email alert
def send_mail_function(image_path):
    msg = MIMEMultipart()
    msg['Subject'] = 'Fire Alert!'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = 'recipient_email@gmail.com'

    text = MIMEText("Warning! A Fire Accident has been reported on ABC Company.")
    msg.attach(text)

    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())

    msg.attach(img)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.login('your_email@gmail.com', 'your_password')
    s.sendmail('your_email@gmail.com', 'recipient_email@gmail.com', msg.as_string())
    s.quit()

def send_whatsapp_alert(image_url):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',  # This number is provided by Twilio
        body='Fire Detected!',
        to='whatsapp:+xxx',
        media_url = [image_url]
    )

    print(message.sid)

def start_configuration():
    global sensitivity_level
    global Fire_Reported
    global Alarm_Status
    global Email_Status
    global Wp_Status
    global start_time
    global configuration_completed
    while True:
        #print the time passed after every 1 second
        print("Time: "+ str(time.time() - start_time))

        # If 10 seconds have passed, increase the sensitivity level
        if time.time() - start_time > 10:
            sensitivity_level = sensitivity_level * 75/100
            print("Sensitivity increased %25 and new level is set to {}".format(sensitivity_level))
            start_time = time.time()
            continue

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
        if int(no_red) > sensitivity_level:
            Fire_Reported = Fire_Reported + 1
            print("!!!")
            print("Fire Detected!")
            print("!!!")

        # Concatenate frames horizontally
        combined_frame = np.hstack((output, frame1))

        combined_frame = cv2.resize(combined_frame, (1540, 800))

        # Display the combined frame
        cv2.imshow("Combined Frame", combined_frame)

        #make it fullscreen
        cv2.namedWindow("Combined Frame", cv2.WND_PROP_FULLSCREEN)

        # If fire is reported, start the alarm and send an email
        if Fire_Reported >= 1:
            if not Alarm_Status:
                #threading.Thread(target=play_alarm_sound_function).start()
                Alarm_Status = True
                print("Was that a correct detection? (Type *y* for Yes and *n* for No)")
                choice = input()
                if choice == 'n':
                    sensitivity_level = sensitivity_level *125/100
                    print("Sensitivity decreased %25 and new level is set to {}".format(sensitivity_level))
                    print("Now trying again with the new sensitivity level...")
                    start_time = time.time()
                    Fire_Reported = 0
                    Alarm_Status = False
                    Email_Status = False
                    configuration_completed = False
                elif choice == 'y':
                    print("The configuration is completed. The system will now start detecting fire with the detected sensitivity level.")
                    start_time = time.time()
                    Fire_Reported = 0
                    Alarm_Status = False
                    Email_Status = False
                    configuration_completed = True
                    break

        # If 'q' is pressed on the keyboard, stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if configuration_completed:
            break

        time.sleep(0.25)

    print("Configuration completed")
    return 0

def start_detector():
    global sensitivity_level
    global Fire_Reported
    global Alarm_Status
    global Email_Status
    global Wp_Status
    global start_time

    # Create 'output' directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    while True:
        print("The fire detection system is active and watching...")
        print("Active time: "+ str(time.time() - start_time))

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
        if int(no_red) > sensitivity_level:
            Fire_Reported = Fire_Reported + 1
            print("!!!")
            print("Fire Detected!")
            print("!!!")
            # Save the frame
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            cv2.imwrite(f'output/fire_{timestamp}.png', frame1)
            cv2.waitKey(1)

        # Concatenate frames horizontally
        combined_frame = np.hstack((output, frame1))

        combined_frame = cv2.resize(combined_frame, (1366, 768))

        # Display the combined frame
        cv2.imshow("Combined Frame", combined_frame)

        #make it fullscreen
        cv2.namedWindow("Combined Frame", cv2.WND_PROP_FULLSCREEN)

        # Display the combined frame
        cv2.imshow("Combined Frame", combined_frame)

        # If fire is reported, start the alarm and send an email
        if Fire_Reported >= 1:
            if not Alarm_Status:
                threading.Thread(target=play_alarm_sound_function).start()
                Alarm_Status = True

            if not Email_Status:
                print("Email is not set up. When setup is complete, email will be sent here.")
                #threading.Thread(target=send_mail_function).start()
                Email_Status = True

            if not Wp_Status:
                print("Whatsapp is not set up. When setup is complete, Whatsapp message will be sent here.")
                #threading.Thread(target=send_whatsapp_alert).start()
                Wp_Status = True

        # If 'q' is pressed on the keyboard, stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        Alarm_Status = False
        Email_Status = False
        Wp_Status = False
        Fire_Reported = 0

        time.sleep(3)

print("Welcome to Fire Detection System")
print("For our system, we have two options for you to choose from:")
print("1. Webcam")
print("2. Video File")
print("Please enter your choice: (Type *1* or *2*)")

# Take input from the user
choice = input()
if choice == '1':
    print("Starting the system with Webcam...")
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    video2 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
elif choice == '2':
    print("Please enter the path of the video file: (e.g. C:\\Users\\User\\Desktop\\Fire_Video.mp4)")
    path = input()
    if path == '':
        print("Path cannot be empty! Please check your path and try again.")
        exit(0)
    print("Starting the system with Video File...")
    video = cv2.VideoCapture(path)
    video2 = cv2.VideoCapture(path)

print()
print("We need to configure our sensitivity level for the system first.")
print("*Note: This process is required for a better accuracy and exception of misreporting.")
print("Please be ready to simulate a fire accident in front of the camera in order to set the sensitivity level.")
print("When you are ready, press *s* to start the configuration process. (Press *q* to quit)")

# Start the configuration process
choice = input()
if choice == 's':
    print("Starting the configuration process...")
    print("The screen above will be the original frame from the video source and the screen below will be the processed frame.")
    print("If the fire is not detected for 10 seconds, the sensitivity level will be increased.")
    #start a timer for 10 seconds
    start = time.time()
    start_configuration()
    print("The configuration is completed.")
    print("Please stop the fire accident and press *s* to start the real fire detection system.")
    print()
    print("*Note: The system will run infinitely until you press *q* or stop the process to quit! (Type *s* to start and *q* to quit)")
    choice = input()
    if choice == 's':
        print("Starting the fire detection system!!!")
        start_time = time.time()
        start_detector()
    elif choice == 'q':
        exit(0)

# Close all OpenCV windows and release the video sources when done
cv2.destroyAllWindows()
video.release()
video2.release()
