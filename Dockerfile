FROM python:3.10-slim

# 필수 시스템 패키지 설치
RUN apt update && apt install -y \
    ffmpeg git curl wget \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    build-essential python3-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/OpenTalker/SadTalker.git /SadTalker


# 모델 다운로드 (checkpoints 폴더에 경로 맞춰 저장)
RUN mkdir -p /SadTalker/checkpoints/gfpgan /SadTalker/checkpoints/wav2lip && \
    cd /SadTalker/checkpoints && \
    wget --timeout=60 --tries=3 --continue -O gfpgan/GFPGANv1.4.pth https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth && \
    wget --timeout=60 --tries=3 --continue -O epoch_20.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth && \
    wget --timeout=60 --tries=3 --continue -O wav2lip/wav2lip.pth https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/wav2lip.pth && \
    wget --timeout=60 --tries=3 --continue -O mapping_00109-model.pth.tar https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar && \
    wget --timeout=60 --tries=3 --continue -O auido2pose_00140-model.pth https://huggingface.co/camenduru/SadTalker/resolve/main/auido2pose_00140-model.pth && \
    wget --timeout=60 --tries=3 --continue -O auido2exp_00300-model.pth https://huggingface.co/camenduru/SadTalker/resolve/main/auido2exp_00300-model.pth && \
    wget --timeout=60 --tries=3 --continue -O facevid2vid_00189-model.pth.tar https://huggingface.co/camenduru/SadTalker/resolve/main/facevid2vid_00189-model.pth.tar



# 작업 디렉토리 설정
WORKDIR /app

# requirements 먼저 복사 (캐시 유지 목적)
COPY requirements.txt ./

# Python 패키지 설치 (캐시됨)
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install git+https://github.com/openai/whisper.git

# 앱 코드 복사 (이 단계만 자주 바뀜)
COPY . /app

# 실행 명령
CMD ["python", "runpod_handler.py"]
