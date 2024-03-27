from ultralytics import YOLO

model = YOLO("models/yolo5_last.pt")

result = model.predict("input/input_video.mp4" ,save=True)

# print(result)

# print("boxes: ")
# for box in result[0].boxes:
#     print(box)