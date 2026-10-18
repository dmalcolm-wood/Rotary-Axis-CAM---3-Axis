#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1

# Prefer a project environment, then the verified macOS Python installation.
if [ -x .venv/bin/python ]; then
  cam_python="$PWD/.venv/bin/python"
elif [ -x /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 ]; then
  cam_python=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
else
  cam_python="$(command -v python3)"
fi
if [ -z "$cam_python" ]; then
  echo "Python 3 was not found. See README.md for installation instructions."
  read -r -p "Press Return to close… "
  exit 1
fi
printf 'Starting Rotary Axis CAM - 3 Axis with %s\n' "$cam_python"
"$cam_python" -u Rotary_Axis_CAM_3_Axis.py
cam_status=$?
if [ "$cam_status" -ne 0 ]; then
  printf '\nApplication exited with code %s. The error is shown above.\n' "$cam_status"
  read -r -p "Press Return to close… "
fi
exit "$cam_status"
