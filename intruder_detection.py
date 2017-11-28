from utilities.tempimage import TempImage
from utilities import sendmail
import argparse
import datetime
import imutils
import time
import pygame
import json
import threading
import cv2

def send_mail_clear_cache(temp_image):
    sendmail.main(from_address, password, to_address, email_subject + " - " + date_string, "./" + temp_image.name + ".jpg", temp_image.name + ".jpg")
    temp_image.cleanup()

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
                help="path to the JSON configuration file")
args = vars(ap.parse_args())

conf = json.load(open(args["conf"]))
min_area = conf["min_area"]

if conf["video"] is None:
    camera = cv2.VideoCapture(0)
    time.sleep(conf["camera_warmup_time"])

else:
    camera = cv2.VideoCapture(conf["video"])

avg = None
frameWithoutRectangles = None
alarm_is_playing = False
pygame.mixer.init()
pygame.mixer.music.load(conf["alarm_sound_path"])
motionCounter = 0
lastUploaded = datetime.datetime.now()
min_upload_seconds = conf["min_upload_seconds"]
min_motion_frames = conf["min_motion_frames"]
send_email = conf["send_email"]
video_width = conf["video_width"]
delta_thresh = conf["delta_thresh"]
from_address = conf["from_email"]
password = conf["with_password"]
to_address = conf["to_email"]
email_subject = conf["email_subject"]

while True:
    (grabbed, frame) = camera.read()
    frameWithoutRectangles = frame
    text = "Normal"
    timestamp = datetime.datetime.now()
    date_string = timestamp.strftime("%d.%m.%Y %H:%M:%S%p")

    if not grabbed:
        break

    # for performance increase, we should set video_width to something like 500 pixels
    # we should also convert image to black&white (for motion detection, color of the image doesn't matter)
    # we should also blur the image to have smooth edges, even 2 consecutive frames aren't exactly the same, so this way we're eliminating too much variations
    frame = imutils.resize(frame, width=video_width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if there is no first frame loaded in avg, we should load it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        continue

    # we accumulate the current frame on frames before
    # calculating "average frame"

    cv2.accumulateWeighted(gray, avg, 0.5)

    # calculating absolute difference between current frame and average frame value
    # this way we adjust to changes, like lighting condition changes in room, new objects added to room, etc...
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    # we threshold delta and we "mark" only pixels that have difference in intensity
    thresh = cv2.threshold(
        frameDelta, delta_thresh, 255, cv2.THRESH_BINARY)[1]
    # dilation is performed, dilation makes it easier to find contours
    thresh = cv2.dilate(thresh, None, iterations=2)
    # we are finding contours
    (_, cnts, _) = cv2.findContours(thresh.copy(),
                                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not cnts:
        if alarm_is_playing:
            alarm_is_playing = False
            pygame.mixer.music.pause()
    else:
        for c in cnts:
            if cv2.contourArea(c) < min_area:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Alert"
            if not alarm_is_playing:
                alarm_is_playing = True
                pygame.mixer.music.play(-1)

    cv2.putText(frame, "Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, date_string,
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    cv2.putText(frameWithoutRectangles, "Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frameWithoutRectangles, date_string,
                (10, frameWithoutRectangles.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    if text == "Alert":
        if(timestamp - lastUploaded).seconds >= min_upload_seconds:
            motionCounter += 1
            if motionCounter >= min_motion_frames:
                if send_email:
                    t = TempImage()
                    cv2.imwrite(t.path, frameWithoutRectangles)
                    # we are sending email on seperate thread
                    threading._start_new_thread(send_mail_clear_cache, (t,))
                    lastUploaded = timestamp
                    motionCounter = 0

    else:
        motionCounter = 0

    if conf["show_video"]:
        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    # uncomment time.sleep line only if you're using video file from disk in order for processing not to be too fast (so you can see what's happening in your video)
    # time.sleep(0.025)
camera.release()
cv2.destroyAllWindows()
