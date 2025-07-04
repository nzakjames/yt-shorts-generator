# runpod_handler.py

import os
import runpod
from handler import handler  # handler.py의 handler(event) import
import torch
import torchvision



print("🚀 RunPod 서버리스 시작")
print("🔥 torch version:", torch.__version__)
print("🔥 torchvision version:", torchvision.__version__)



runpod.serverless.start({"handler": handler})
