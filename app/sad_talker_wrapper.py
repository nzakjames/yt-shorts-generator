import subprocess
import os
import glob
from pathlib import Path

def generate_talking_video(image_path, audio_path, work_dir):
    sad_path = Path("/SadTalker")
    inference_path = sad_path / "inference.py"

    image_path = Path(image_path)
    audio_path = Path(audio_path)
    work_dir = Path(work_dir)

    # 입력 유효성 확인
    if not image_path.is_file():
        raise FileNotFoundError(f"이미지 파일이 존재하지 않습니다: {image_path}")
    if not audio_path.is_file():
        raise FileNotFoundError(f"오디오 파일이 존재하지 않습니다: {audio_path}")
    if not inference_path.is_file():
        raise FileNotFoundError(f"inference.py 파일이 존재하지 않습니다: {inference_path}")

    # 결과 디렉토리 생성
    work_dir.mkdir(parents=True, exist_ok=True)

    # SadTalker 실행
    print(f"▶ SadTalker 실행 중...\n이미지: {image_path}\n오디오: {audio_path}\n출력: {work_dir}")
    try:
        result = subprocess.run(
            [
                "python3", str(inference_path),
                "--driven_audio", str(audio_path),
                "--source_image", str(image_path),
                "--enhancer", "gfpgan",
                "--result_dir", str(work_dir),
                "--preprocess", "full"
            ],
            check=True,
            cwd=str(sad_path),  # 🔴 핵심: SadTalker 내부 상대경로 기준 보장
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ 실행 완료\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 실패\nSTDERR:\n{e.stderr}")
        raise RuntimeError("SadTalker 실행 실패") from e

    # 결과 mp4 파일 검색
    video_files = list(work_dir.rglob("*.mp4"))
    if not video_files:
        raise FileNotFoundError("SadTalker 실행 후 생성된 영상(mp4)을 찾을 수 없습니다.")
    if len(video_files) > 1:
        video_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return str(video_files[0])
