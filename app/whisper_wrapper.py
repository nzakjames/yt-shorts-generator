import whisper
import os

_model = None  # 전역 변수로 모델 캐시

def get_model():
    global _model
    if _model is None:
        print("🧠 Whisper 모델 로딩 중...")
        _model = whisper.load_model("tiny")
        print("✅ Whisper 모델 로딩 완료")
    return _model

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def transcribe_audio(audio_path, output_dir):
    print(f"🎧 자막 생성 시작: {audio_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일이 존재하지 않습니다: {audio_path}")

    model = get_model()  # 여기서 로드 (최초 1회만)

    try:
        result = model.transcribe(audio_path)
    except Exception as e:
        print(f"❌ Whisper transcribe 오류: {str(e)}")
        raise

    srt_path = os.path.join(output_dir, "subtitles.srt")
    try:
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"]):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                f.write(f"{i+1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(segment["text"].strip() + "\n\n")
        print(f"✅ SRT 저장 완료: {srt_path}")
    except Exception as e:
        print(f"❌ SRT 저장 중 오류: {str(e)}")
        raise

    return srt_path
