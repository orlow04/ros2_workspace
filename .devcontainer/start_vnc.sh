#!/bin/bash
pkill Xvfb 2>/dev/null
pkill x11vnc 2>/dev/null

Xvfb :1 -screen 0 1920x1080x24 &
sleep 1
x11vnc -display :1 -passwd ros123 -listen 0.0.0.0 -xkb -forever &

export DISPLAY=:1
export LIBGL_ALWAYS_SOFTWARE=1
echo "VNC ready at vnc://localhost:5900 (password: ros123)"