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
def write_logs(time_logs,cnt):
    for file, time_log in time_logs:
        print "analyzing %s" % file.name
        for time in time_log:
            file.write(str(time[0:2]) + "\n")
        file.write("Face moved %d times towards the camera" % (cnt))
        file.close()


if __name__ == "__main__":
        subject_name = raw_input("What is the subject's name? ")
        file1 = "%s\\recorded\\00109.avi" % (dir_path)
        # create video stream object
        cap1 = cv2.VideoCapture("./recorded/00109.avi")
        cap1.set(15, 0.1)
        start = time.clock()
        result = []
        time_log = []
        face_found = False
        last = 0
        frame_count = 0
        diff = 5
        roundby = 0.01
        cnt = 0
        temp_frameNo = 0
        round = lambda n: n - n % roundby if n % roundby < .05 else n + roundby

        #Running only for 1 camera as of now

        while (cap1.isOpened()):
                time_stamp = round(time.clock() - start)
                rets, frames = cap1.read()
                
                dim = (640, 420)
 
                # perform the actual resizing of the image and show it
                temp_frameNo += 1

                if divmod(temp_frameNo,30)[1]==0 and rets:
                    frames = cv2.resize(frames, dim, interpolation = cv2.INTER_AREA)
                    
                    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
                    
                    faces = FACE_CASCADE.detectMultiScale(gray,1.1,5)

                    for (x,y,w,h) in faces:
                            cv2.rectangle(frames,(x,y),(x+w,y+h),(0,255,0),2)

                    #
                    cv2.imshow('Camera(%d)' % 1, frames)

                    frame_count += 1
                        
                    if len(faces)==1:
                            time_log.append((frame_count,time_stamp,1))
                            last = frame_count
                    else:
                            time_log.append((frame_count,time_stamp,0))
                            last = frame_count


                    if frame_count>1 and (time_log[frame_count-1][-1]==0 and time_log[frame_count-2][-1]==1):
                            cnt += 1
                        

                    if cv2.waitKey(1) & 0xFF == ord('q'):  # number of milliseconds to display frame for.
                            break                              # not sure if this should be tuned.

        time_log.append((frame_count,round(time.clock() - start),0))
        result.append(time_log)
        cap1.release()

        cv2.destroyAllWindows()
        video_files = [file1]

        print "Now analyzing videos, please wait"
        analyze_files = [open(f.replace("avi", "txt").replace("recorded", "analyzed"), 'w+') for f in video_files]
        write_logs(zip(analyze_files, result),cnt)
        print("Exiting")
