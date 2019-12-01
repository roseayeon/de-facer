import torch
import numpy as np
import cv2
from PIL import Image, ImageDraw
import torchvision.transforms.functional as F
import sys 
sys.path.append('../server')
from const import *
import face_recognition

def grab_frames(video_path, targets_path, output_dir):
  # encoding target face
  targets_encoding_our = []
  targets_encoding_dlib = []
  for target_path in targets_path:
    target_img = cv2.cvtColor(cv2.imread(target_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    # dlib
    face_locations = face_recognition.face_locations(target_img)
    targets_encoding_dlib.append(face_recognition.face_encodings(target_img, face_locations)[0])

    # our
    target_img = Image.fromarray(target_img)
    target_aligned = mtcnn(target_img)[0]
    targets_encoding_our.append(resnet(torch.stack([target_aligned]).to(device)).detach().cpu())

  cap = cv2.VideoCapture(video_path)
  count = 0
  while True:
    count += 1
    success, frame = cap.read()
    if not success:
      break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    
    # dlib preprocess
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # MTCNN + FaceNet
    small_frame = Image.fromarray(small_frame)
    
    boxes, face_probs = mtcnn.detect(small_frame)
    if boxes is None:
      boxes = []
    frame_img = Image.fromarray(frame)
    frame_w, frame_h = frame_img.size

    faces = []
    for box in boxes:
      box = [
        int(max(box[0]*4, 0)),
        int(max(box[1]*4, 0)),
        int(min(box[2]*4, frame_w)),
        int(min(box[3]*4, frame_h)),
      ]

      face = frame_img.crop(box).resize((FACE_SIZE, FACE_SIZE), 2)
      face = prewhiten(F.to_tensor(np.float32(face)).to(device))
      faces.append(face)

    if len(faces) != 0:
      encodings = resnet(torch.stack(faces)).detach().cpu()
      for encoding, box, prob in zip(encodings, boxes, face_probs):
        # if detected face prob is < THRESHOLD, don't recognize as face
        if prob < FACE_THRESHOLD:
          continue

        box = [
          int(max(box[0]*4, 0)),
          int(max(box[1]*4, 0)),
          int(min(box[2]*4, frame_w)),
          int(min(box[3]*4, frame_h)),
        ]

        target_detected = False
        for target_encoding in targets_encoding_our: 
          face_diff = (encoding - target_encoding).norm().item()
          if face_diff <= DIFF_THRESHOLD:
            target_detected = True
            break

        if target_detected:
          cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 10)
        else:
          cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 2)

    # using dlib
    for (location, encoding) in zip(face_locations, face_encodings):
      top, right, bottom, left = location
      distances = face_recognition.face_distance(targets_encoding_dlib, encoding)
      min_dist = min(distances)
      # Draw a box around the face
      if min_dist < 0.5:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 10)
      else:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)


    cv2.imwrite(output_dir+"/"+str(count)+".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))


  cap.release()

if __name__ == "__main__":
  grab_frames("data/1/allaboutyou.mp4", ['data/1/iu.png'], 'output/1')
  grab_frames("data/2/champions.mp4", ['data/2/faker.png'], 'output/2')
  grab_frames("data/3/group.mp4", ['data/3/jaeeui.png'], 'output/3')
  grab_frames("data/4/hanhwa.mp4", ['data/4/hanhwa.png'], 'output/4')
  grab_frames("data/5/iuina.mp4", ['data/5/iu.png'], 'output/5')
  grab_frames("data/6/munnam.mp4", ['data/6/parkkyoung.png'], 'output/6')
  grab_frames("data/7/sdamsdam.mp4", ['data/7/hodong.png'], 'output/7')
  grab_frames("data/8/yesoryes.mp4", ['data/8/jeongyeon.png'], 'output/8')
  grab_frames("data/9/koreanbros.mp4", ['data/9/koreanbros.png'], 'output/9')
  grab_frames("data/10/beautyinside.mp4", ['data/10/hyojoo.png'], 'output/10')
