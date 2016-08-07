import cv2
import time
import os
import re
import sys, smtplib


# Analyzes every .avi file provided to it. Returns a list of time_logs, which
# follows a pattern of face detected, face looked away ... face ends.
def analyze_videos(videos, fps, in_dir):
    cascade_file_name = "haarcascade_frontalface_default.xml"
    cascade_file_name_2 = "haarcascade_profileface.xml"
    cascade_file_name_3 = "haarcascade_frontalface_alt.xml"
    face_cascade = cv2.CascadeClassifier(cascade_file_name)
    face_cascade_2 = cv2.CascadeClassifier(cascade_file_name_2)
    face_cascade_3 = cv2.CascadeClassifier(cascade_file_name_3)
    if face_cascade.empty():
        print 'Could not load face cascade, is it not at %s/%s?' % (os.getcwd(), cascade_file_name)
        quit()
    start = time.clock()
    result = []
    for video in videos:
        cap = cv2.VideoCapture("%s/%s" % (in_dir, video))
        if not cap.isOpened():
            print "Could not open file: %s, moving onto next file" % video
            continue
        else:
            print "Analyzing file: %s" % video

        totalframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(totalframes)

        time_log = []
        label = []
        temp = []
        cnt = 0
        timeinstance = []
        face_found = False

        ret, frame = cap.read()
        last = 0  # last frame we saw a face
        frame_count = 0
        diff = 5  # 5 frame tolerance range.
        roundby = .01
        round = lambda n: n - n % roundby if n % roundby < roundby / 2 else n + roundby - n % roundby
        while ret:

            sys.stdout.write("Progress: %f%% \r" %(frame_count*100/totalframes))
            sys.stdout.flush()
            time_stamp = round(frame_count / fps)
            # Manipulate frames here.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces1 = face_cascade.detectMultiScale(gray, 1.1, 5)
            faces2 = face_cascade_2.detectMultiScale(gray, 1.1, 5)
            faces3 = face_cascade_3.detectMultiScale(gray, 1.1, 5)
            #
            frame_count += 1.0

            if len(faces1)==1 or len(faces2)==1 or len(faces3)==1:
                time_log.append(time_stamp)
                label.append(1)
                last = frame_count
            else:
                time_log.append(time_stamp)
                label.append(0)
                last = frame_count
            if frame_count>4 and (label[int(frame_count)-1]==0 and label[int(frame_count)-2]==1 and label[int(frame_count)-3]==1 and label[int(frame_count)-4]==1):
                cnt += 1
                timeinstance.append(time_stamp)
            
            ret, frame = cap.read()
        time_log.append(round(frame_count / fps))
        result.append(time_log)
        temp.append(timeinstance)
    return cnt,temp,result


# Formats times into a csv friendly string, where the left column contains the
# time where a face was detected, and the right column contains when the face
# 'looked away'
def format_times_positive(times, faces, msg ="Looked at cam,Looked away\nTimes looked,"):
    even = len(times) if len(times) % 2 == 0 else len(times) - 1
    result = "%s %s\nIntervals,(s)\n" % (msg, faces)
    for i in range(0, even, 2):
        result += "%s,%s\n" % (str(times[i]).strip(), str(times[i + 1]).strip())
    return result


# Does the same as format_times_positive, except the left column contains when a face
# looked away and the right column contains when it looked back.
def format_times_negative(times, faces):
    return format_times_positive(times[1:], faces - 1, "Looked away,Looked at cam\nTimes looked away,")


# Reads the analysis file, renames the last _flag, and writes the formatted csv file
def write_files(file_pairs, cnt, line_ending, positivep, out_dir):
    func = format_times_positive if positivep else format_times_negative
    for f, log in file_pairs:
        if len(log) < 2:
            print "Did not find any time intervals in %s, skipping" % f
            continue
        target = open(os.path.join(out_dir, f.replace(f.split('_')[-1],
                                                      '%s.csv' % line_ending)), 'w')
        target.write(func(log, round(cnt/2)))


# Effect: Searches for files that end with some flag (a flag is an _'flag'.txt)
# Then, it will create a formatted csv file, replacing the flag with "++" or "--" to
# denote whether it's for when faces look at camera or away from camera.
if __name__ == "__main__":
    in_dir = "C:\\Users\\rams1\\Desktop\\DrLevac\\FaceDetection\\Face_Detectionv6\\recorded_fresh\\"
    out_dir = "analyzed"
    positive = re.compile(".*_%s.avi" % 1) #raw_input("Looking for positive matches in files ending with? "))
    positive_fps = 15 # = int(raw_input("FPS of positive videos? (Usually 30, if using video camera) "))
    negative = re.compile(".*_%s.avi" % 2) #raw_input("Looking for negative matches in files ending with? "))
    negative_fps = 15 # = int(raw_input("FPS of negative videos? (Usually 15, if using record_videos.py) "))
    files = os.listdir(in_dir)
    positive_files = filter(positive.match, files)
    negative_files = filter(negative.match, files)
    print "Analyzing positive videos"
    cnt1, temp1, video1 = analyze_videos(positive_files, positive_fps, in_dir)
    positive_pairs = zip(positive_files, temp1)
    print "Formatting positive files"
    write_files(positive_pairs, cnt1, '++', True, out_dir)
    print "Analyzing negative videos"
    cnt2, temp2, video2 = analyze_videos(negative_files, negative_fps, in_dir)
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login("10bec093@nirmauni.ac.in","moonytonks")
    server.sendmail("10bec093@nirmauni.ac.in","rams16592@gmail.com","Part 1 finished.")
    negative_pairs = zip(negative_files, temp2)
    print "Formatting negative files"
    write_files(negative_pairs, cnt2, '--', False, out_dir)
    print "All done!"
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login("10bec093@nirmauni.ac.in","moonytonks")
    server.sendmail("10bec093@nirmauni.ac.in","rams16592@gmail.com","Part 2 finished.")
