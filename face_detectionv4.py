"""http://docs.opencv.org/3.1.0/d7/d8b/tutorial_py_face_detection.html#gsc.tab=0"""
import cv2
import time
import os

# Get the current directory we're in
dir_path = os.getcwd().replace("\\", "/")
cur_date = time.strftime("%d-%m_%H-%M-%S")
# Load the face cascade. If it's empty, most likely not in the right spot.
cascade_file_name = "haarcascade_frontalface_alt.xml"
FACE_CASCADE = cv2.CascadeClassifier("%s/%s" % (dir_path, cascade_file_name))
if FACE_CASCADE.empty():
    print "Could not load face cascade, is it not at %s/%s?" % (dir_path, cascade_file_name)
    quit()


# Simply logs all the time stamps. Note that time_logs is a list of tuples
# of (File name ot write to, time_log)
def write_logs(time_logs,cnt,timeinstance):
        for file, time_log in time_logs:
            print "analyzing %s" % file.name
            for time in time_log:
                file.write(str(time) + "\n")
            file.write("Face moved %d times from the Front Camera" % (cnt[0])+"\n")
            file.write("Time at which face moved from the Front Camera:\n")
            for instance in timeinstance[0]:
                file.write("%2.2f" % (instance)+"\n")
            if len(cnt)==2:
                file.write("Face moved %d times from the Side Camera" % (cnt[1])+"\n")
                file.write("Time at which face moved from the Side Camera:\n")
                for instance in timeinstance[1]:
                    file.write("%2.2f" % (instance)+"\n")
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

        cam1 = 0 if face_cam else 2
        cam2 = 1 if face_cam else 3

        # create video stream object
        cap1 = cv2.VideoCapture(2)
        cap2 = cv2.VideoCapture(3) if no_cameras == 2 else None

        print "The recorded footage will be saved in recorded/%s_%s_(1 or 2)" % (subject_name, cur_date)
        print "The analyzed files will be saved in analyzed/%s_%s_(1 or 2)" % (subject_name, cur_date)

        file1 = "%s/recorded/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 1)
        file2 = "%s/recorded/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 2)

        caps = [cap1, cap2] if cap2 else [cap1]

        fourcc_codec = cv2.VideoWriter_fourcc(*'MJPG')
        resolution = (int(cap1.get(3)), int(cap1.get(4)))
        fps = 5
        outs = [cv2.VideoWriter(file1,fourcc_codec,fps,resolution), cv2.VideoWriter(file2,fourcc_codec,fps,(int(cap2.get(3)), int(cap2.get(4))))] if cap2\
                else cv2.VideoWriter(file1,fourcc_codec,fps,resolution)

        # Initializations
        start = time.clock()
        time_log1 = []
        time_log2 = []
        time_log = []
        face_found = False
        last = 0
        frame_count = 0
        diff = 5
        roundby = 0.01
        cnt1 = 0
        cnt2 = 0
        timeinstance1 = []
        timeinstance2 = []
        timeinstance = []
        round = lambda n: n - n % roundby if n % roundby < .05 else n + roundby

        # Cameras are run simultaneously 
        while (cap.isOpened() for cap in caps):
                time_stamp = round(time.clock() - start)
                rets, frames = [a for a in zip(*[cap.read() for cap in caps])]
                               
                for out,frame,i in zip(outs,frames,range(len(caps))):
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.equalizeHist(gray)
                    faces = FACE_CASCADE.detectMultiScale(
                            gray,
                            scaleFactor = 1.1,
                            minNeighbors = 5
                    )
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.imshow('Camera(%d)' % i, frame)
                    out.write(frame)
                    if i == 0:
                        if len(faces)==1:
                            time_log1.append((frame_count,time_stamp,1))
                            last = frame_count
                        else:
                            time_log1.append((frame_count,time_stamp,0))
                            last = frame_count
                        if frame_count>1 and (time_log1[frame_count-1][-1]==0 and time_log1[frame_count-2][-1]==1):
                            cnt1 += 1
                            timeinstance1.append(time_stamp)

                    if i == 1:
                        if len(faces)==1:
                            time_log2.append((frame_count,time_stamp,1))
                            last = frame_count
                        else:
                            time_log2.append((frame_count,time_stamp,0))
                            last = frame_count
                        if frame_count>1 and (time_log2[frame_count-1][-1]==0 and time_log2[frame_count-2][-1]==1):
                            cnt2 += 1
                            timeinstance2.append(time_stamp)
                    
                frame_count += 1

                if cv2.waitKey(1) & 0xFF == ord('q'):  # number of milliseconds to display frame for.
                    break                              # not sure if this should be tuned.

        # Storing the values
        if len(caps)==2:
            time_log1.append((frame_count,round(time.clock() - start),0))
            time_log2.append((frame_count,round(time.clock() - start),0))
            time_log.append(time_log1)
            time_log.append(time_log2)
            timeinstance.append(timeinstance1)
            timeinstance.append(timeinstance2)
            cnt = [cnt1, cnt2]
        else:
            time_log1.append((frame_count,round(time.clock() - start),0))
            time_log.append(time_log1)
            timeinstance.append(timeinstance1)
            cnt = [cnt1]

        for cap,out in caps,outs:
              cap.release()
              out.release()

        cv2.destroyAllWindows()
        video_files = [file1] if not cap2 else [file1, file2]

        print "Now analyzing videos, please wait"
        analyze_files = [open(f.replace("avi", "txt").replace("recorded", "analyzed"), 'w+') for f in video_files]
        write_logs(zip(analyze_files, time_log),cnt,timeinstance)
        print("Exiting")
