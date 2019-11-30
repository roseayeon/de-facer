import cv2
import torchvision.transforms.functional as F
import numpy as np
from PIL import Image
import torch
from const import *

class FaceRealTime():
  def __init__(self, url, targets_path, replace_path):
    self.cap = cv2.VideoCapture(url)
    self.count = 0

    # encoding target face
    self.targets_encoding = []
    for target_path in targets_path:
      target_img = cv2.imread(target_path, cv2.IMREAD_COLOR)
      target_img = Image.fromarray(cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB))
      target_aligned = mtcnn(target_img)[0]
      self.targets_encoding.append(resnet(torch.stack([target_aligned]).to(device)).detach().cpu())

    # replace image
    self.replace_img = None
    if replace_path is not None:
      self.replace_img = cv2.imread(replace_path, cv2.IMREAD_UNCHANGED)
      self.replace_alpha = self.replace_img[:,:,3] / 255.0
      self.replace_alpha = cv2.merge((self.replace_alpha, self.replace_alpha, self.replace_alpha))
      self.replace_img = cv2.cvtColor(self.replace_img, cv2.COLOR_BGRA2RGB)

  def __del__(self):
    self.cap.release()

  def get_frame(self):
    success, frame = self.cap.read()
    if not success:
      return None

    self.count += 1
    # reduce fps because we cannot use batch
    if self.count % 3 != 0:
      return None
  
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    small_frame = Image.fromarray(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))
  
    # Detect faces
    boxes, _ = mtcnn.detect(small_frame) # decrease of face size
    if boxes is None:
      return frame

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_img = Image.fromarray(frame)
    frame_w, frame_h = frame_img.size
    
    # Draw box of face
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
  
    encodings = resnet(torch.stack(faces)).detach().cpu()
    for encoding, box in zip(encodings, boxes):
      box = [
        int(max(box[0]*4, 0)),
        int(max(box[1]*4, 0)),
        int(min(box[2]*4, frame_w)),
        int(min(box[3]*4, frame_h)),
      ]

      target_detected = False
      for target_encoding in self.targets_encoding: 
        face_diff = (encoding - target_encoding).norm().item()
        if face_diff <= DIFF_THRESHOLD:
          target_detected = True
          break

      if not target_detected:
        w = box[2]-box[0]
        h = box[3]-box[1]
        if self.replace_img is None:
          # Blur face
          face = frame[box[1]:box[3], box[0]:box[2]]
          # select blur method
          #blurred_face = cv2.GaussianBlur(face, (19,19), 0)
          blurred_face = cv2.resize(face, (0,0), fx=REDUCE_RATE, fy=REDUCE_RATE)
          blurred_face = cv2.resize(blurred_face, (w,h), interpolation=cv2.INTER_LINEAR)
          frame[box[1]:box[3], box[0]:box[2]] = blurred_face
        else:
          # Replacement
          face = frame[box[1]:box[3], box[0]:box[2]]
          cover_face = cv2.resize(self.replace_img, (w, h))
          alpha = cv2.resize(self.replace_alpha, (w, h))
          frame[box[1]:box[3], box[0]:box[2]] = face * (1-alpha) + cover_face * alpha
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

  def get_jpg_bytes(self):
    frame = self.get_frame()
    if frame is None:
      return None
    return cv2.imencode('.jpg', frame)[1].tobytes() 

if __name__ == "__main__":
  FaceRealTime(0, ["../media/target.jpg"], None).get_jpg_bytes()
