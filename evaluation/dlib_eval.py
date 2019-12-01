import torch
import numpy as np
import cv2
from PIL import Image, ImageDraw
import torchvision.transforms.functional as F
import sys 
import face_recognition
import time

def process_video(video_path, targets_path, output_path):
  start_ms = int(time.time() *1000)
  # encoding target face
  cap = cv2.VideoCapture(video_path)
  video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  origin_fps = cap.get(cv2.CAP_PROP_FPS)

  targets_encoding_dlib = []
  for target_path in targets_path:
    target_img = cv2.cvtColor(cv2.imread(target_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(target_img)
    targets_encoding_dlib.append(face_recognition.face_encodings(target_img, face_locations)[0])

  count = 0
  writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), origin_fps, (video_w,video_h))
  while True:
    count += 1
    success, frame = cap.read()
    if not success:
      break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    
    # dlib preprocess
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    # using dlib
    for (location, encoding) in zip(face_locations, face_encodings):
      top, right, bottom, left = location
      top *= 4
      right *= 4
      bottom *= 4
      left *= 4
      distances = face_recognition.face_distance(targets_encoding_dlib, encoding)
      min_dist = min(distances)
      # Draw a box around the face
      if min_dist < 0.4:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 10)
      else:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

  cap.release()
  print (int(time.time() *1000) - start_ms)

if __name__ == "__main__":
  process_video("data/10/beautyinside.mp4", ['data/10/hyojoo.png'], 'output/10')

