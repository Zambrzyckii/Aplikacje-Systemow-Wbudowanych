#!/bin/bash

cam=rpicam
command -v rpicam-hello >/dev/null || cam=libcamera

stamp=$(date +%H%M%S)

case "$1" in
preview)
    "$cam-hello" -t 10000
    ;;
photo)
    "$cam-jpeg" -o "photo_$stamp.jpg"
    ;;
video)
    "$cam-vid" -t 10000 -o "video_$stamp.h264"
    ;;
timelapse)
    "$cam-still" -t 20000 --timelapse 2000 -o "frame_$stamp%03d.jpg"
    ffmpeg -framerate 2 -i "frame_$stamp%03d.jpg" "timelapse_$stamp.mp4"
    ;;
stream)
    "$cam-vid" -t 0 --inline --listen -o tcp://0.0.0.0:8888
    ;;
*)
    echo "usage: $0 preview | photo | video | timelapse | stream"
    ;;
esac
