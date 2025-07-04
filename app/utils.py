import os
import requests

from pathlib import Path
import urllib.request
import subprocess
from dotenv import load_dotenv


load_dotenv()  # .env 파일 로드



def download_models():
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN is not set.")

    models = 
    {
      "gfpgan/GFPGANv1.4.pth": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        "min_size": 100000000
      },
      "epoch_20/G_ema.pth": {
        "url": "https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth",
        "min_size": 300000000
      },
      "wav2lip/wav2lip.pth": {
        "url": "https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/wav2lip.pth",
        "min_size": 200000000
      },
      "epoch_20.pth": {
        "url": "https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth",
        "min_size": 300000000
      },
      "mapping_00109-model.pth.tar": {
        "url": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
        "min_size": 10000000
      }
    }

    for path, info in models.items():
        out_path = f"/SadTalker/checkpoints/{path}"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        # 파일 존재 여부 및 크기 확인
        if os.path.exists(out_path):
            file_size = os.path.getsize(out_path)
            if file_size >= info["min_size"]:
                print(f"[✓] Skipping {path} (already downloaded, size={file_size})")
                continue
            else:
                print(f"[!] File {path} exists but too small ({file_size} < {info['min_size']}), re-downloading...")

        print(f"[↓] Downloading {path} ...")
        result = subprocess.run([
            "curl", "--fail", "-L", "--retry", "3",
            "-H", f"Authorization: Bearer {token}",
            "-o", out_path, info["url"]
        ], check=False)

        if result.returncode != 0:
            raise RuntimeError(f"Download failed: {path}")
        elif os.path.getsize(out_path) < info["min_size"]:
            raise RuntimeError(f"Downloaded file too small: {path}")

        print(f"[✓] Downloaded {path}")





def download_image(url, output_dir):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 에러 상태코드 자동 예외 처리
    except requests.RequestException as e:
        raise Exception(f"이미지 다운로드 실패: {e}")

    # 파일 확장자 추정
    ext = url.split("?")[0].split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "jpg"  # 기본 확장자

    img_path = os.path.join(output_dir, f"image.{ext}")
    with open(img_path, "wb") as f:
        f.write(response.content)

    return img_path
