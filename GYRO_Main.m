clear all
clc

rpi = raspi('169.254.80.188','pi','raspberry');
scanI2CBus(rpi,'i2c-1');
sensor1 = i2cdev(rpi,'i2c-1','0x6B');
sensor2 = i2cdev(rpi,'i2c-1','0x1D');
Gain = 0.07*0.02;

X = 0; Y = 0; Z = 0;

i = 0;
tic;
while i < 100
    i = i + 1;
    XL = readRegister(sensor1,hex2dec('28'),'uint8');
    XH = readRegister(sensor1,hex2dec('29'),'uint8');
    YL = readRegister(sensor1,hex2dec('2A'),'uint8');
    YH = readRegister(sensor1,hex2dec('2B'),'uint8');
    ZL = readRegister(sensor1,hex2dec('2C'),'uint8');
    ZH = readRegister(sensor1,hex2dec('2D'),'uint8');
    tempx = double(XH)*256 + double(XL); tempx(tempx>32768)=tempx-65536;
    tempy = double(YH)*256 + double(YL); tempy(tempy>32768)=tempy-65536;
    tempz = double(ZH)*256 + double(ZL); tempz(tempz>32768)=tempz-65536;
    X(i+1) = (X(i)) + tempx*Gain;
    Y(i+1) = (Y(i)) + tempy*Gain;
    Z(i+1) = (Z(i)) + tempz*Gain;
    fprintf('%f      %f      %f\n',X(i+1),Y(i+1),Z(i+1))
end
toc;