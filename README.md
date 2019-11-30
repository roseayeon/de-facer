# De-facer

*KAIST 2019 Fall CS470 Introduction to Artificial Intelligence Team 13 Final Project*

Service to detect the faces from video and ***de-face***(replace with other image or blur) them.


## Motivation
As _YouTube_ is actively used and personal YouTubers are increasing, we often see private broadcasts on the streets. We also take authentication shots on the street to post on _Instagram_. However, in these cases, my face may appear in other people's broadcasts, and others’ faces may appear in my Instagram photos. We came up with an idea like this to address this issue.

## Models
We used the [pytorch implementation](https://github.com/timesler/facenet-pytorch) of ["FaceNet: A Unified Embedding for Face Recognition and Clustering"](https://arxiv.org/abs/1503.03832).

## Features

### Video de-facing
Sample bluh bluh

### Real-time de-facing
Sample bluh bluh

## Installation

### Requirements

* Python 3.5+
* macOS or Linux
* Node.js 12+

### Installing

```bash
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
