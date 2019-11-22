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

FACE_SIZE = 160
DIFF_THRESHOLD = 0.8
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, min_face_size=20, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def process_video(video_path, targets_path, replace_path, output_path):
  cap = cv2.VideoCapture(video_path)
  count = 0
  targets_encoding = []
  for target_path in targets_path:
    target_img = cv2.imread(target_path, cv2.IMREAD_COLOR)
    target_img = Image.fromarray(cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB))
    target_aligned = mtcnn(target_img)
    target_encoding = resnet(target_aligned.to(device)).detach().cpu()
    targets_encoding.append(target_encoding)
  
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
      frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
  
      # Detect faces
      boxes, _ = mtcnn.detect(small_frame) # decrease of face size
      
      # Draw box of face
      faces = []
      for box in boxes:
          box = [
              int(max(box[0]*4, 0)),
              int(max(box[1]*4, 0)),
              int(min(box[2]*4, frame.size[0])),
              int(min(box[3]*4, frame.size[1])),
          ]
  
          face = frame.crop(box).resize((face_size, face_size), 2)
          face = prewhiten(F.to_tensor(np.float32(face)).to(device))
          faces.append(face)
  
      embedding = resnet(torch.stack(faces)).detach().cpu()
      frame_draw = frame.copy()
      draw = ImageDraw.Draw(frame_draw)
      for embed, box in zip(embedding, boxes):
          box = [
              int(max(box[0]*4, 0)),
              int(max(box[1]*4, 0)),
              int(min(box[2]*4, frame.size[0])),
              int(min(box[3]*4, frame.size[1])),
          ]
          face_diff = (embed - target_embedding[0]).norm().item()
          #print (count, face_diff)
          if face_diff > diff_threshold:
              draw.rectangle(box, outline=(255, 0, 0), width=6)
      
      # Add to frame list
      # doubled frame ti restore fps
      frames_tracked.append(frame_draw.resize((640, 360), Image.BILINEAR))
      frames_tracked.append(frame_draw.resize((640, 360), Image.BILINEAR))
      #if count%100 == 0:
      #    print ("frame:", count)
    else:
      raise Exception('Reading video should be success')

  cap.release()

  #print('\rTracking frame: {}'.format(count))
  writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), len(frames_tracked), (640,360))
  for frame in frames_tracked:
    writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
  writer.release()

  #print('\nDone')
  cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video('video.mp4', ['target.jpg'], '', 'output.avi')

