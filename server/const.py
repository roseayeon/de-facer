from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import time

# Parameter
DEBUG = False 
MAX_FRAME = 99999999 # fast exit for testing
FACE_SIZE = 160 # cropped face size
REDUCE_RATE = 0.03 # blurring resize factor
DIFF_THRESHOLD = 0.8 # face embedding distance threshold
FACE_THRESHOLD = 0.97 # face prob threshold
MAX_FACES_LEN = 200 # max batch length of FaceNet

# Global variable
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, min_face_size=20, thresholds=[0.6, 0.75, 0.9], device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def prewhiten(x):
  mean = x.mean()
  std = x.std()
  std_adj = std.clamp(min=1.0/(float(x.numel())**0.5))
  y = (x - mean) / std_adj
  return y

def get_ms():
  return int(time.time()*1000.0)

def print_msg(start_ms, msg):
  if DEBUG:
    print (msg, get_ms() - start_ms)
