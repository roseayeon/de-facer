# De-facer

*KAIST 2019 Fall CS470 Introduction to Artificial Intelligence Team 13 Final Project*

Service to detect the faces from video and ***de-face***(replace with other images or blur) them.


## Motivation
Nowadays, you can easily see people who broadcast on the streets. As private broadcasts (ex. _YouTube_) are becoming more common, the issue of portrait rights infringement is also getting serious. 

Therefore, we defined our problem as '**How can we protect others’ portrait portraits in the video?**'. It is important that we must show broadcasters but not others. We came up with an idea to 1) detect faces, 2) match face with target images and 3) blur/replace other faces except for target faces. We also dealt with real-time conditions.

## Models
We used the [pytorch implementation](https://github.com/timesler/facenet-pytorch) of ["FaceNet: A Unified Embedding for Face Recognition and Clustering"](https://arxiv.org/abs/1503.03832).

## Flow
<img src="figures/diagram.png" width="600">

## Features

### Video de-facing (with replace image)
<img src="figures/mamison.gif" width="600">
<img src="figures/harrypotter.gif" width="600">

### Real-time de-facing (with Blur)
<img src="figures/realtime.gif" width="600">

## Installation

### Requirements

* Python 3.5+
* macOS or Linux
* Node.js 12+

### Installing

```bash
apt-get install nodejs
pip3 install torch torchvision flask flask_cors facenet-pytorch opencv-python google-cloud-storage

export GOOGLE_APPLICATION_CREDENTIALS="[PATH TO server/service_key.json]" # Or use own setting
```

## Usage

### Run server
```bash
cd server
python3 manage.py
```

### Web
```bash
cd web-page
npm install
npm start
```

## Parameter
You can change the parameter as you wish in ```server/const.py```.
```bash
MAX_FRAME = 99999999 # fast exit for testing
FACE_SIZE = 160 # cropped face size
REDUCE_RATE = 0.03 # blurring resize factor
DIFF_THRESHOLD = 0.8 # face embedding distance threshold
FACE_THRESHOLD = 0.97 # face prob threshold
MAX_FACES_LEN = 200 # max batch length of FaceNet
```

## Reference
- [Ant Design](https://ant.design/)
- F. Schroff, D. Kalenichenko, J. Philbin. _FaceNet: A Unified Embedding for Face Recognition and Clustering_, arXiv:1503.03832, 2015. [PDF](https://arxiv.org/pdf/1503.03832)
- K. Zhang, Z. Zhang, Z. Li and Y. Qiao. _Joint Face Detection and Alignment Using Multitask Cascaded Convolutional Networks_, IEEE Signal Processing Letters, 2016. [PDF](https://arxiv.org/ftp/arxiv/papers/1604/1604.02878.pdf)
