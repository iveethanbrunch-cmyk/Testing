#!/bin/bash
# Usage: bash render_job/render_shot.sh <shot>   (run from repo root)
# Renders one Blender Cycles camera shot of the rig at 1280x720, 12 fps, and encodes it to render_job/out/<shot>.mkv
set -euo pipefail
SHOT="$1"; R="$(cd "$(dirname "$0")" && pwd)"
python3 -m venv /tmp/bvenv && /tmp/bvenv/bin/pip install -q bpy
cd "$R" && S="$R" OUT=frames SHOTS="$SHOT" RX=1280 RY=720 SAMPLES=8 FPS=12 /tmp/bvenv/bin/python blend/shots.py 2>&1 | grep --line-buffered FRAME
ffmpeg -y -loglevel error -framerate 12 -i "frames/$SHOT/%04d.png" -c:v ffv1 -level 3 "out/$SHOT.mkv"
echo "DONE $SHOT $(ls frames/$SHOT | wc -l) frames"
