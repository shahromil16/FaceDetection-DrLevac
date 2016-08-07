clear all
clc

curr = pwd;
folder_name = uigetdir('C:\Users\rams1\Desktop\DrLevac\FaceDetection\v7');
cd(folder_name);
filename1 = dir('*_1.avi');
[cnt1,seen_frame1,seen_time1] = videoAnalysis(filename1.name);

filename2 = dir('*_2.avi');
[cnt2,seen_frame2,seen_time2] = videoAnalysis(filename2.name);
cd(curr);