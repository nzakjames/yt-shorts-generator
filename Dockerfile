FROM python:3.10-slim

# 필수 시스템 패키지 설치
RUN apt update && apt install -y \
    ffmpeg git curl wget \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    build-essential python3-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/OpenTalker/SadTalker.git /SadTalker

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
