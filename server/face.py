import cv2
import torchvision.transforms.functional as F
import numpy as np
from PIL import Image, ImageDraw
import torch
from const import *

def process_video(video_path, targets_path, replace_path, output_path):
  start_ms = get_ms()
  cap = cv2.VideoCapture(video_path)
  video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  origin_fps = cap.get(cv2.CAP_PROP_FPS)
  count = 0

  # encoding target face
  targets_encoding = []
  for target_path in targets_path:
    target_img = cv2.imread(target_path, cv2.IMREAD_COLOR)
    target_img = Image.fromarray(cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB))
    target_aligned = mtcnn(target_img)[0]
    targets_encoding.append(resnet(torch.stack([target_aligned]).to(device)).detach().cpu())

  # replace image
  if replace_path is not None:
    replace_img = cv2.imread(replace_path, cv2.IMREAD_UNCHANGED)
    replace_alpha = replace_img[:,:,3] / 255.0
    replace_alpha = cv2.merge((replace_alpha, replace_alpha, replace_alpha))
    replace_img = cv2.cvtColor(replace_img, cv2.COLOR_BGRA2RGB)
  
  print_msg (start_ms, "capture start")
  frames_tracked = []
  batches = []
  while True:
    success, frame = cap.read()
    if success:
      count += 1
  
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
      small_frame = Image.fromarray(small_frame)
  
      batches.append(small_frame)
      
      # add to frame list
      frames_tracked.append(frame)
    else:
      # video is finished
      break

    # for develop
    if DEBUG and count > MAX_FRAME:
      break

  cap.release()

  # detect faces
  boxes, _ = mtcnn.detect(batches)
  print_msg(start_ms, "mtcnn end")

  faces = []
  start_idx = 0
  writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), origin_fps, (video_w,video_h))
  for (i, frame) in enumerate(frames_tracked):
    # crop recognized face 
    if boxes[i] is None:
      boxes[i] = []
    for box in boxes[i]:
      box = [
        int(max(box[0]*4, 0)),
        int(max(box[1]*4, 0)),
        int(min(box[2]*4, video_w)),
        int(min(box[3]*4, video_h)),
      ]

      face = cv2.resize(frame[box[1]:box[3], box[0]:box[2]], (FACE_SIZE, FACE_SIZE), interpolation=cv2.INTER_AREA)
      face = prewhiten(F.to_tensor(face).to(device))
      faces.append(face)

    if len(faces) < MAX_FACES_LEN:
      continue

    encodings = resnet(torch.stack(faces)).detach().cpu()
    print_msg(start_ms, "resnet end")
    idx = 0
    for j in range(start_idx, i+1):
      frame = frames_tracked[j]
      for box in boxes[j]:
        box = [
          int(max(box[0]*4, 0)),
          int(max(box[1]*4, 0)),
          int(min(box[2]*4, video_w)),
          int(min(box[3]*4, video_h)),
        ]
        encoding = encodings[idx]
        idx += 1

        target_detected = False
        for target_encoding in targets_encoding: 
          face_diff = (encoding - target_encoding).norm().item()
          if face_diff <= DIFF_THRESHOLD:
            target_detected = True
            break

        if not target_detected:
          w = box[2]-box[0]
          h = box[3]-box[1]
          if replace_path is None:
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
            cover_face = cv2.resize(replace_img, (w, h))
            alpha = cv2.resize(replace_alpha, (w, h))
            frame[box[1]:box[3], box[0]:box[2]] = face * (1-alpha) + cover_face * alpha
      writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
    
    faces = []
    start_idx = i+1

  if len(faces) != 0:
    encodings = resnet(torch.stack(faces)).detach().cpu()
    print_msg (start_ms, "resnet end")
    idx = 0
    for j in range(start_idx, len(frames_tracked)):
      frame = frames_tracked[j]
      for box in boxes[j]:
        box = [
          int(max(box[0]*4, 0)),
          int(max(box[1]*4, 0)),
          int(min(box[2]*4, video_w)),
          int(min(box[3]*4, video_h)),
        ]
        encoding = encodings[idx]
        idx += 1

        target_detected = False
        for target_encoding in targets_encoding: 
          face_diff = (encoding - target_encoding).norm().item()
          if face_diff <= DIFF_THRESHOLD:
            target_detected = True
            break

        if not target_detected:
          w = box[2]-box[0]
          h = box[3]-box[1]
          if replace_path is None:
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
            cover_face = cv2.resize(replace_img, (w, h))
            alpha = cv2.resize(replace_alpha, (w, h))
            frame[box[1]:box[3], box[0]:box[2]] = face * (1-alpha) + cover_face * alpha
      writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))


  writer.release()
  print_msg(start_ms, "finish")

  cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video('../media/video.mp4', ['../media/target.jpg', '../media/target.jpg'], None, 'output.mp4')

