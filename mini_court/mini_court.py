import cv2
import sys 
sys.path.append("../")

import constants
from utils import (
    convert_pixel_distance_to_meters,
    convert_meters_to_pixel_distance
)

class MiniCourt:
    def __init__(self, frame):
        self.drawing_rectangle_width = 250
        self.drawing_rectangle_height = 450
        self.buffer = 50
        self.padding_court = 20

        self.set_canvas_background_box_position(frame)
        self.set_mini_court_position()

    def set_court_drawing_key_points(self):
        drawing_key_points = [0]*28

        #point 0
        drawing_key_points[0], drawing_key_points[1] = int(self.court_start_x), int(self.court_start_y)
        #point 1
        drawing_key_points[2], drawing_key_points[3] = int(self.court_end_x), int(self.court_start_y)
        #point 2
        drawing_key_points[4] = int(self.court_start_x)
        drawing_key_points[5] = self.court_start_y + convert_meters_to_pixel_distance(
            constants.HALF_COURT_LINE_HEIGHT*2,
            constants.DOUBLE_LINE_WIDTH,
            self.court_drawing_width
        )

        #point 3
        drawing_key_points[6]
        drawing_key_points[7] 

    def set_mini_court_position(self):
        self.court_start_x = self.start_x + self.padding_court
        self.court_start_y = self.start_y + self.padding_court
        self.court_end_x = self.end_x - self.padding_court
        self.court_end_y = self.end_y - self.padding_court

        self.court_drawing_width = self.court_end_x - self.court_start_x

    def set_canvas_background_box_position(self, frame):
        frame = frame.copy()

        self.end_x = frame.shape[1] - self.buffer
        self.end_y = self.buffer + self.drawing_rectangle_height
        self.start_x = self.end_x - self.drawing_rectangle_width
        self.start_y = self.end_y - self.drawing_rectangle_height
