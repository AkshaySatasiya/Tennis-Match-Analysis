from utils import (read_video,
                   save_video)
from trackers import (PlayerTracker,
                      BallTracker)
from court_line_detector import CourtLineDetector
from mini_court import MiniCourt
import cv2

def main():
    # Read Video
    input_video_path = "input/input_video.mp4"
    video_frames = read_video(input_video_path)

    # Detect Players and Ball
    player_tracker = PlayerTracker(model_path="yolov8x")
    ball_tracker = BallTracker(model_path="models/yolo5_last.pt")

    player_detections = player_tracker.detect_frames(video_frames,
                                                     read_from_stub=True,
                                                     stub_path='tracker_stubs/player_detection.pkl'
                                                     )

    ball_detections = ball_tracker.detect_frames(video_frames,
                                                     read_from_stub=True,
                                                     stub_path='tracker_stubs/ball_detection.pkl'
                                                     )
    ball_detections = ball_tracker.interpolate_ball_position(ball_detections)
    
    # Court line detector model
    court_model_path = "models/keypoints_model.pth"
    court_line_detector = CourtLineDetector(court_model_path)
    court_keypoints = court_line_detector.predict(video_frames[0])

    # Choose players
    player_detections = player_tracker.choose_and_filter_player(court_keypoints, player_detections)

    # Minicourt
    mini_court = MiniCourt(video_frames[0])

    # Detect ball shots
    ball_shot_frames = ball_tracker.get_ball_shot_frame(ball_detections)
    print(ball_shot_frames)

    # Convert position to mini court positions
    player_mini_court_detection,ball_mini_court_detection = mini_court.convert_bounding_boxes_to_mini_court_coordinates(player_detections, 
                                                                                                                        ball_detections, 
                                                                                                                        court_keypoints)




    # Draw Bounding Box
    output_video_frames = player_tracker.draw_bboxes(video_frames, player_detections)
    output_video_frames = ball_tracker.draw_bboxes(output_video_frames, ball_detections)


    # Draw court keypoints 
    output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames,court_keypoints)

    #draw mini court
    output_video_frames = mini_court.draw_mini_court(output_video_frames)
    output_video_frames = mini_court.draw_points_on_mini_court(output_video_frames, player_mini_court_detection)
    output_video_frames = mini_court.draw_points_on_mini_court(output_video_frames, ball_mini_court_detection, color=(0,255,255))


    #draw frame number on top left corner
    for i,frame in enumerate(output_video_frames):
        cv2.putText(frame, f"Frame: {i}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    # Save Video
    save_video(output_video_frames, "output_videos/output_video_2.avi")

if __name__ == "__main__":
    main()