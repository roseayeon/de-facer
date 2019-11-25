import cv2
from torchvision import transforms
import torchvision.transforms.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np
from PIL import Image, ImageDraw

def prewhiten(x):
  mean = x.mean()
  std = x.std()
  std_adj = std.clamp(min=1.0/(float(x.numel())**0.5))
  y = (x - mean) / std_adj
  return y

MAX_FRAME = 240 # for testing
FACE_SIZE = 160
REDUCE_RATE = 0.03
DIFF_THRESHOLD = 0.9
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, min_face_size=20, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def process_video(video_path, targets_path, replace_path, output_path):
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
  if replace_path != "":
    replace_img = cv2.imread(replace_path, cv2.IMREAD_UNCHANGED)
    replace_alpha = replace_img[:,:,3] / 255.0
    replace_alpha = cv2.merge((replace_alpha, replace_alpha, replace_alpha))
    replace_img = cv2.cvtColor(replace_img, cv2.COLOR_BGRA2RGB)
  
  frames_tracked = []
  while cap:
    success, frame = cap.read()
    if success:
      # change fps
      count += 1
      if count % 2 == 0:
        continue
  
      small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
      small_frame = Image.fromarray(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      frame_img = Image.fromarray(frame)
      frame_w, frame_h = frame_img.size
  
      # Detect faces
      boxes, _ = mtcnn.detect(small_frame) # decrease of face size
      
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
        for target_encoding in targets_encoding: 
          face_diff = (encoding - target_encoding).norm().item()
          #print (count, face_diff)
          if face_diff <= DIFF_THRESHOLD:
            target_detected = True
            break

        if not target_detected:
          w = box[2]-box[0]
          h = box[3]-box[1]
          if replace_path == "":
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
      
      # Add to frame list
      frames_tracked.append(frame)
    else:
      raise Exception('Reading video should be success')

    #Shortcut
    if count > MAX_FRAME:
      break

  cap.release()

  #print('\rTracking frame: {}'.format(count))
  writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), origin_fps/2, (video_w,video_h))
  for frame in frames_tracked:
    writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
  writer.release()

  #print('\nDone')
  cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video('video.mp4', ['target.jpg'], '', 'output.avi')

