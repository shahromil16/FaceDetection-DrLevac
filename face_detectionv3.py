"""http://docs.opencv.org/3.1.0/d7/d8b/tutorial_py_face_detection.html#gsc.tab=0"""
import cv2
import time
import os

# Get the current directory we're in
dir_path = os.getcwd().replace("\\", "/")
cur_date = time.strftime("%d-%m_%H-%M-%S")
# Load the face cascade. If it's empty, most likely not in the right spot.
cascade_file_name = "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier("%s/%s" % (dir_path, cascade_file_name))
if FACE_CASCADE.empty():
    print "Could not load face cascade, is it not at %s/%s?" % (dir_path, cascade_file_name)
    quit()


# Helper method to make a video writer out from the given capture.
# Getting the correct fourcc is really tricky. Pass in -1 to cv2.VideoWriter_fourcc
# to see a list of all available fourcc codes.
def make_out(capture, file_name):
    resolution = (int(capture.get(3)), int(capture.get(4)))
    fps = 15
    fourcc_codec = cv2.VideoWriter_fourcc(*'MJPG') # this is hard to tune correctly
    # store video to output
    out = cv2.VideoWriter(file_name, fourcc_codec, fps, resolution)
    return out


# Captures from either 1 or two cameras, and stores their output into
# the recorded directory as .avi files. Note that .avi files can only support
# up to 2GB of files.
def capture_videos(subject_name, cap1, cap2=None):
    file1 = "%s/recorded/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 1)
    file2 = "%s/recorded/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 2)
    caps = [cap1, cap2] if cap2 else [cap1]
    outs = [make_out(cap1, file1), make_out(cap2, file2)] if cap2 \
        else [make_out(cap1, file1)]
    try:
        while all([x.isOpened() for x in caps]):
            rets, frames = [a for a in zip(*[cap.read() for cap in caps])]
            if not all(rets):
                print('retval returned false. Possible threshold error')
                break
            for out, frame, i in zip(outs, frames, range(len(caps))):
                out.write(frame)
                cv2.imshow('Camera(%d)' % i, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # number of milliseconds to display frame for.
                break                              # not sure if this should be tuned.
    except KeyboardInterrupt:
        exit

    for cap, out in zip(caps, outs):
        out.release()
        cap.release()

    cv2.destroyAllWindows()
    return [file1] if not cap2 else [file1, file2]


##################################################################################
## Code doesnt run into the analysis function thus needs to be brought together ##
##################################################################################

# Analyzes every .avi file provided to it. Returns a list of time_logs, which
# follows a pattern of face detected, face looked away ... face ends.
def analyze_videos(videos):
    start = time.clock()
    # validate
    if FACE_CASCADE.empty():
        print "Could not open facial recognition classifier, ensure .xml file is good"
        quit()
    result = []
    for video in videos:
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            print "Could not open file: %s, moving onto next file" % video
            continue

        time_log = []
        face_found = False

        ret, frame = cap.read()
        last = 0  # last frame we saw a face
        frame_count = 0
        diff = 5  # 5 frame tolerance range.
        roundby = .01
        round = lambda n: n - n % roundby if n % roundby < .05 else n + roundby - n % roundby
        while ret:
            time_stamp = round(time.clock() - start)
            # Manipulate frames here.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(
                gray,
                scaleFactor = 1,
                minNeighbors = 5
                )
            #
            frame_count += 1
            if len(faces) > 0 and not face_found:
                face_found = True
                time_log.append(time_stamp)
                last = frame_count
            elif len(faces) > 0:
                last = frame_count
            elif frame_count - last > diff and face_found:
                face_found = False
                time_log.append(time_stamp)
                last = frame_count
            ret, frame = cap.read()
        time_log.append(round(time.clock() - start))
        result.append(time_log)
    return result


# Simply logs all the time stamps. Note that time_logs is a list of tuples
# of (File name ot write to, time_log)
def write_logs(time_logs):
    for file, time_log in time_logs:
        print "analyzing %s" % file.name
        for time in time_log:
            file.write(str(time) + "\n")
        file.write("Number of faces detected: %d" % (len(time_log) // 2))
        file.close()


if __name__ == "__main__":
    subject_name = raw_input("What is the subject's name? ")
    no_cameras = raw_input("How many cameras? (1/2): ")
    while no_cameras != "1" and no_cameras != "2":
        no_cameras = raw_input("Input either 1 or 2: ")
    no_cameras = int(no_cameras)
    face_cam = raw_input("Are you using the computer's web cam? (y/n): ")
    while face_cam != "y" and face_cam != "n":
        face_cam = raw_input("Input either y or n: ")
    face_cam = True if face_cam == "y" else False
    # As far as I can tell, the 'camera number' corresponds as follows:
    # 0 is the computers web cam, 1 is the first other web cam, 2 is the second,
    # so on and so forth, followed by any 'virtual' web cams.
    cam1 = 0 if face_cam else 1
    cam2 = 1 if face_cam else 2

    # create video stream object
    cap1 = cv2.VideoCapture(cam1)
    cap2 = cv2.VideoCapture(cam2) if no_cameras == 2 else None

    print "The recorded footage will be saved in recorded/%s_%s_(1 or 2)" % (subject_name, cur_date)
    print "The analyzed files will be saved in analyzed/%s_%s_(1 or 2)" % (subject_name, cur_date)
    video_files = capture_videos(subject_name, cap1, cap2)
    print "Now analyzing videos, please wait"
    analyze_files = [open(f.replace("avi", "txt").replace("recorded", "analyzed"), 'w+') for f in video_files]
    time_logs = analyze_videos(video_files)
    write_logs(zip(analyze_files, time_logs))
    print("Exiting")
