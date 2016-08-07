%edit FaceTrackingUsingKLTExample
%edit FaceTrackingWebcamExample

function [cnt,seen_frame,seen_time] = videoAnalysis(filename)

faceDetector = vision.CascadeObjectDetector();
pointTracker = vision.PointTracker('MaxBidirectionalError', 2);

videoFileReader = vision.VideoFileReader(filename);
videoFrame      = step(videoFileReader);
numPts = 0;
frameCount = 0;
checker = [];
% frameSize = size(videoFrame);
videoPlayer  = vision.VideoPlayer('Position',...
    [100 100 [size(videoFrame, 2), size(videoFrame, 1)]+30]);
while ~isDone(videoFileReader)
    videoFrame = step(videoFileReader);
    videoFrameGray = rgb2gray(videoFrame);
    frameCount = frameCount + 1;
    if numPts < 10
        bbox = faceDetector.step(videoFrameGray);
        if ~isempty(bbox)
            points = detectMinEigenFeatures(videoFrameGray, 'ROI', bbox(1, :));
            xyPoints = points.Location;
            numPts = size(xyPoints,1);
            release(pointTracker);
            initialize(pointTracker, xyPoints, videoFrameGray);
            oldPoints = xyPoints;
            bboxPoints = bbox2points(bbox(1, :));  
            bboxPolygon = reshape(bboxPoints', 1, []);
            videoFrame = insertShape(videoFrame, 'Polygon', bboxPolygon, 'LineWidth', 3);
            checker = [checker, 1];
        else
            checker = [checker,0];
        end
    else
        [xyPoints, isFound] = step(pointTracker, videoFrameGray);
        visiblePoints = xyPoints(isFound, :);
        oldInliers = oldPoints(isFound, :);
        numPts = size(visiblePoints, 1);       
        if numPts >= 10
            [xform, oldInliers, visiblePoints] = estimateGeometricTransform(...
                oldInliers, visiblePoints, 'similarity', 'MaxDistance', 4);            
            bboxPoints = transformPointsForward(xform, bboxPoints);
            bboxPolygon = reshape(bboxPoints', 1, []);            
            videoFrame = insertShape(videoFrame, 'Polygon', bboxPolygon, 'LineWidth', 3);
            oldPoints = visiblePoints;
            setPoints(pointTracker, oldPoints);
            checker = [checker, 1];
        else
            checker = [checker, 0];
        end
    end
    step(videoPlayer, videoFrame);
end

x = checker;
i = find(diff(x)); n = [i numel(x)] - [0 i]; c = arrayfun(@(X) X-1:-1:0, n , 'un',0);
cnts = cat(2,c{:}); t1=find(cnts>5);
t2 = find(checker(t1));
t3 = t1(t2);
cnt = 1;
seen_frame = t3(1);
t3d = diff(t3);
for i=2:length(t3d)
    if t3d(i)==1 && t3d(i-1)~=1
        cnt = cnt + 1;
        seen_frame = [seen_frame, t3(i)];
    end
end
seen_time = seen_frame./30;


release(videoFileReader);
release(videoPlayer);
release(pointTracker);
close all;

end