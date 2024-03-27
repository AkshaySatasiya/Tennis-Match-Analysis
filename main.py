from utils import (read_video,
                   save_video)
from trackers import PlayerTracker

def main():
    # Read Video
    input_video_path = "input/input_video.mp4"
    video_frames = read_video(input_video_path)

    # Detect Players
    player_tracker = PlayerTracker(model_path="yolov8x")
    player_detections = player_tracker.detect_frames(video_frames)

    # Draw Bounding Box of players
    output_video_frames = player_tracker.draw_bboxes(video_frames, player_detections)


    # Save Video
    save_video(output_video_frames, "output_videos/output_video.avi")

if __name__ == "__main__":
    main()