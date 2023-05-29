import cv2
import numpy as np
import smtplib
import playsound
import threading

Alarm_Status = False
Email_Status = False
Fire_Reported = 0

def play_alarm_sound_function():
    while True:
        playsound.playsound('alarm-sound.mp3', True)

def send_mail_function():
    recipientEmail = "Enter_Recipient_Email"
    recipientEmail = recipientEmail.lower()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("Enter_Your_Email (System Email)", 'Enter_Your_Email_Password (System Email')
        server.sendmail('Enter_Your_Email (System Email)', recipientEmail, "Warning A Fire Accident has been reported on ABC Company")
        print("sent to {}".format(recipientEmail))
        server.close()
    except Exception as e:
        print(e)

# video = cv2.VideoCapture(0)
video = cv2.VideoCapture("Fire_Video.mp4")  # If you want to use webcam, use Index like 0,1.
video2 = cv2.VideoCapture("Fire_Video.mp4")  # If you want to use a video file, provide the file name.

while True:
    grabbed1, frame1 = video.read()
    grabbed2, frame2 = video2.read()

    if not grabbed1 or not grabbed2:
        break

    frame1 = cv2.resize(frame1, (960, 540))
    #cv2.imshow("output1", frame1)

    frame2 = cv2.resize(frame2, (960, 540))

    blur = cv2.GaussianBlur(frame2, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = [18, 50, 50]
    upper = [35, 255, 255]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    mask = cv2.inRange(hsv, lower, upper)

    output = cv2.bitwise_and(frame2, hsv, mask=mask)

    no_red = cv2.countNonZero(mask)

    if int(no_red) > 15000:
        Fire_Reported = Fire_Reported + 1
        print("Fire Detected!")

    #cv2.imshow("output2", output)

    # Concatenate frames horizontally
    combined_frame = np.vstack((output, frame1))

    cv2.imshow("Combined Frame", combined_frame)

    if Fire_Reported >= 1:
        if not Alarm_Status:
            threading.Thread(target=play_alarm_sound_function).start()
            Alarm_Status = True

        if not Email_Status:
            threading.Thread(target=send_mail_function).start()
            Email_Status = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
video.release()
video2.release()
