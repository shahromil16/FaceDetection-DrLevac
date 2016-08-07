"""http://docs.opencv.org/3.1.0/d7/d8b/tutorial_py_face_detection.html#gsc.tab=0"""
import cv2
import time
import os

# Get the current directory we're in
dir_path = os.getcwd().replace("\\", "/")
cur_date = time.strftime("%d-%m_%H-%M-%S")


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

        cam1 = 1 if face_cam else 0
        cam2 = 0 if face_cam else 1

        # create video stream object
        cap1 = cv2.VideoCapture(cam1)
        cap2 = cv2.VideoCapture(cam2) if no_cameras == 2 else None

        print "The recorded footage will be saved in recorded_fresh/%s_%s_(1 or 2)" % (subject_name, cur_date)

        file1 = "%s/recorded_fresh/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 1)
        file2 = "%s/recorded_fresh/%s_%s_%d.avi" % (dir_path, subject_name, cur_date, 2)

        caps = [cap1, cap2] if cap2 else [cap1]

        fourcc_codec = cv2.VideoWriter_fourcc(*'MJPG')
        resolution = (640,480)
        fps = 25
        outs = [cv2.VideoWriter(file1,fourcc_codec,fps,resolution), cv2.VideoWriter(file2,fourcc_codec,fps,resolution)] if cap2 \
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
        while all([cap.isOpened() for cap in caps]):
                time_stamp = round(time.clock() - start)
                rets, frames = [a for a in zip(*[cap.read() for cap in caps])]
                               
                for out,frame,i in zip(outs,frames,range(len(caps))):
                    cv2.imshow('Camera(%d)' % i, frame)
                    out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('p'):
                        raw_input("Paused. Press Enter to continue:")
                        
                if cv2.waitKey(1) & 0xFF == ord('q'):  # number of milliseconds to display frame for.
                    break                              # not sure if this should be tuned.

        for cap,out in caps,outs:
              cap.release()
              out.release()

        cv2.destroyAllWindows()
        video_files = [file1] if not cap2 else [file1, file2]
