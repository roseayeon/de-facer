import cv2
from torchvision import transforms
import torchvision.transforms.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np
from PIL import Image, ImageDraw
import time

def prewhiten(x):
  mean = x.mean()
  std = x.std()
  std_adj = std.clamp(min=1.0/(float(x.numel())**0.5))
  y = (x - mean) / std_adj
  return y

MAX_FRAME = 1500 # for testing
FACE_SIZE = 160
REDUCE_RATE = 0.03
DIFF_THRESHOLD = 0.9
MAX_FACES_LEN = 200
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, min_face_size=20, thresholds=[0.6, 0.75, 0.9], device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def get_ms():
  return int(time.time()*1000.0)

def process_video(video_path, targets_path, replace_path, output_path):
  start_time = get_ms()
  cap = cv2.VideoCapture(video_path)
  video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  origin_fps = cap.get(cv2.CAP_PROP_FPS)
  count = 0
  # encoding target face
  targets_img = []
  for target_path in targets_path:
    target_img = cv2.imread(target_path, cv2.IMREAD_COLOR)
    target_img = Image.fromarray(cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB))
    targets_img.append(target_img)

  targets_aligned = mtcnn(targets_img)
  targets_aligned = [target[0] for target in targets_aligned]
  targets_encoding = resnet(torch.stack(targets_aligned).to(device)).detach().cpu()

  # replace image
  if replace_path is not None:
    replace_img = cv2.imread(replace_path, cv2.IMREAD_UNCHANGED)
    replace_alpha = replace_img[:,:,3] / 255.0
    replace_alpha = cv2.merge((replace_alpha, replace_alpha, replace_alpha))
    replace_img = cv2.cvtColor(replace_img, cv2.COLOR_BGRA2RGB)
  
  print ("capture start", get_ms()-start_time) 
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
    if count > MAX_FRAME:
      break

  cap.release()
  # detect faces
  boxes, _ = mtcnn.detect(batches)
  print ("mtcnn end", get_ms()-start_time) 

  writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), origin_fps, (video_w,video_h))
  faces = []
  start_idx = 0
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
    print ("resnet end", get_ms() - start_time)
    idx = 0
    for j in range(start_idx, i+1):
      frame = frames_tracked[j]
      for box in boxes[j]:
        encoding = encodings[idx]
        idx += 1

        box = [
          int(max(box[0]*4, 0)),
          int(max(box[1]*4, 0)),
          int(min(box[2]*4, video_w)),
          int(min(box[3]*4, video_h)),
        ]

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
    print ("resnet end", get_ms() - start_time)
    idx = 0
    for j in range(start_idx, len(frames_tracked)):
      frame = frames_tracked[j]
      for box in boxes[j]:
        encoding = encodings[idx]
        idx += 1

        box = [
          int(max(box[0]*4, 0)),
          int(max(box[1]*4, 0)),
          int(min(box[2]*4, video_w)),
          int(min(box[3]*4, video_h)),
        ]

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
  print("finish", get_ms()-start_time)

  cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video('../media/video.mp4', ['../media/target.jpg'], None, 'output.avi')

