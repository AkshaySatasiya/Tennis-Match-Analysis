from ultralytics import YOLO
import cv2
import pickle
import pandas as pd

class BallTracker:
    
    def __init__(self,model_path) :
        self.model = YOLO(model_path)

    def interpolate_ball_position(self, ball_positions):
        ball_positions  =[x.get(1,[]) for x in ball_positions]

        #convert list into pandas dataframe
        df_ball_position = pd.DataFrame(ball_positions, columns=['x1','y1','x2','y2'])

        #interpolate missing values
        df_ball_position = df_ball_position.interpolate()
        df_ball_position = df_ball_position.bfill()

        ball_positions = [{1:x} for x in df_ball_position.to_numpy().tolist()]

        return ball_positions

    def get_ball_shot_frame(self, ball_positions):
        ball_positions  =[x.get(1,[]) for x in ball_positions]
        #convert list into pandas dataframe
        df_ball_position = pd.DataFrame(ball_positions, columns=['x1','y1','x2','y2'])

        df_ball_position['mid_y'] = (df_ball_position['y1']+df_ball_position['y2'])/2
        df_ball_position['mid_y_rolling_mean'] = df_ball_position['mid_y'].rolling(window=10, min_periods=1, center=False).mean()
        df_ball_position['delta_y'] = df_ball_position['mid_y_rolling_mean'].diff()
        df_ball_position['ball_hit'] = 0
        
        minimum_change_frames_for_hit = 25
        for i in range(0, len(df_ball_position)-int(minimum_change_frames_for_hit*1.2)):
            negative_position_change = df_ball_position['delta_y'].iloc[i] >0 and df_ball_position['delta_y'].iloc[i+1] < 0
            positive_position_change = df_ball_position['delta_y'].iloc[i] <0 and df_ball_position['delta_y'].iloc[i+1] > 0

            if positive_position_change or negative_position_change:
                change_count = 0
                for change_frame in range(i+1, i+int(minimum_change_frames_for_hit*1.2)+1):
                    negative_position_change_following_frame = df_ball_position['delta_y'].iloc[i] >0 and df_ball_position['delta_y'].iloc[change_frame] < 0
                    positive_position_change_following_frame = df_ball_position['delta_y'].iloc[i] <0 and df_ball_position['delta_y'].iloc[change_frame] > 0

                    if negative_position_change and negative_position_change_following_frame:
                        change_count += 1
                    elif positive_position_change and positive_position_change_following_frame:
                        change_count += 1

                if change_count > minimum_change_frames_for_hit-1:
                    df_ball_position['ball_hit'].iloc[i] = 1 

        frame_nums_with_ball_hits = df_ball_position[df_ball_position['ball_hit']==1].index.to_list()

        return frame_nums_with_ball_hits


    def detect_frames(self,frames, read_from_stub=False, stub_path=None):
        ball_detections = []

        if read_from_stub and stub_path is not None:
            with open(stub_path, 'rb') as f:
                ball_detections = pickle.load(f)
            return ball_detections

        for frame in frames:
            player_dict = self.detect_frame(frame)
            ball_detections.append(player_dict)

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(ball_detections, f)

        return ball_detections

    def detect_frame(self,frame):
        results = self.model.predict(frame,conf=0.15)[0]

        ball_dict = {}
        for box in results.boxes:
            result = box.xyxy.tolist()[0]
            ball_dict[1] = result

        return ball_dict
    
    def draw_bboxes(self, video_frames, ball_detections):
        output_video_frames = []
        for frame, ball_dict in zip(video_frames,ball_detections):
            # Draw Bounding Boxes
            for track_id, bbox in ball_dict.items():
                x1,y1,x2,y2 = bbox
                cv2.putText(frame, f"Ball ID: {track_id}", (int(bbox[0]), int(bbox[1]-10 )), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)

            output_video_frames.append(frame)

        return output_video_frames