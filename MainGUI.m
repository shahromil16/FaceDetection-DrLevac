function varargout = MainGUI(varargin)
% MAINGUI MATLAB code for MainGUI.fig
%      MAINGUI, by itself, creates a new MAINGUI or raises the existing
%      singleton*.
%
%      H = MAINGUI returns the handle to a new MAINGUI or the handle to
%      the existing singleton*.
%
%      MAINGUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MAINGUI.M with the given input arguments.
%
%      MAINGUI('Property','Value',...) creates a new MAINGUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before MainGUI_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to MainGUI_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help MainGUI

% Last Modified by GUIDE v2.5 03-Aug-2016 00:42:25

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @MainGUI_OpeningFcn, ...
    'gui_OutputFcn',  @MainGUI_OutputFcn, ...
    'gui_LayoutFcn',  [] , ...
    'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before MainGUI is made visible.
function MainGUI_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to MainGUI (see VARARGIN)
% Choose default command line output for MainGUI
handles.output = hObject;
global PAUSE RESUME

START = get(handles.start,'Value');
set(handles.pause,'enable','off');
set(handles.resume,'enable','off');
set(handles.start,'enable','off');
set(handles.start,'Value',0);

IP = inputdlg('Enter rPi IP address:',...
             'IP', [1 50]);

rpi = raspi(IP,'pi','raspberry');
scanI2CBus(rpi,'i2c-1');
sensor1 = i2cdev(rpi,'i2c-1','0x6B');
%sensor2 = i2cdev(rpi,'i2c-1','0x1D');
Gain = 0.07*0.02;

guidata(hObject, handles);
% UIWAIT makes MainGUI wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = MainGUI_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;

% --- Executes on button press in start.
function start_Callback(hObject, eventdata, handles)
% hObject    handle to start (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global PAUSE RESUME FINISH
%disp(get(hObject,'Value'))
START = get(hObject,'Value');
RESUME = 1;
PAUSE = 0;
FINISH = 0;

if START == 1
    set(handles.pause,'enable','on');
    set(handles.resume,'enable','on');
    subjname = get(handles.edit1,'String');
    set(handles.start,'enable','off');
end

% i=0;
% while 1==1
%     pause(0.1)
%     if FINISH==1
%         i=i+1
%     else
%         continue;
%     end
% end

a = datestr(datetime('now'));
a = strrep(a,' ','_'); a = strrep(a,':','-');
a = strcat(subjname,'_',a);
name1 = strcat(a,'_1.avi');
name2 = strcat(a,'_2.avi');

C = webcamlist;
IndexC = strfind(C, 'Logitech HD Pro Webcam C920');
Index = find(not(cellfun('isempty', IndexC)));

if length(Index)<2
    errordlg('One or No Logitech Camera Detected. Please recheck connection before pressing Start. Press Ok to continue.');
end

pause(0.1);

if START==1 && RESUME==1
    
    v1 = VideoWriter(name1); v2 = VideoWriter(name2);
    open(v1); open(v2);
    cam1 = webcam((1)); 
    cam2 = webcam((2));
    imaqreset;
    temp1=zeros(480,640,3);
    h1=imshow(uint8(temp1),'Parent',handles.axes1); h2=imshow(uint8(temp1),'Parent',handles.axes2);
    hold on;
    frames = 0;

    while FINISH==0 
        vid1 = snapshot(cam1);
        vid2 = snapshot(cam2);
        %data1 = snapshot(vid1);      %takes one frame at a time from the buffer
        %data2 = snapshot(vid2);
        set(h1,'Cdata',vid1);
        set(h2,'Cdata',vid2);
        if RESUME==1
            frames = frames + 1;
%             img1{frames} = vid1;
%             img2{frames} = vid2;
            writeVideo(v1,vid1); writeVideo(v2,vid2);
        else
            continue;
        end
    end
    clear vid1;
    clear vid2;
    %stop(vid1); stop(vid2);
    %delete(vid1); delete(vid2);
end

% for i=1:length(img1);
%     pause(0.01);
%     writeVideo(v1,img1{i}); writeVideo(v2,img2{i});
% end

close(v1); close(v2);
imaqreset;
close all;


% --- Executes on button press in pause.
function pause_Callback(hObject, eventdata, handles)
% hObject    handle to pause (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global PAUSE RESUME
PAUSE = get(handles.pause,'Value');
RESUME = get(handles.resume,'Value');

function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit1 as text
%        str2double(get(hObject,'String')) returns contents of edit1 as a double


% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in resume.
function resume_Callback(hObject, eventdata, handles)
% hObject    handle to resume (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of resume
global PAUSE RESUME
PAUSE = get(handles.pause,'Value');
RESUME = get(handles.resume,'Value');


% --- Executes on button press in finish.
function finish_Callback(hObject, eventdata, handles)
% hObject    handle to finish (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global FINISH
FINISH = get(hObject,'Value');


% --- Executes on button press in gyro.
function gyro_Callback(hObject, eventdata, handles)
% hObject    handle to gyro (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global GYRO 
GYRO = get(hObject,'Value');

if GYRO == 1
    h = msgbox('Look at the center');
end