import os
from pathlib import Path

# ✅ 개발 환경에서만 .env 로딩
if Path(".env").exists():
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env 로딩됨 (개발 환경)")
else:
    print("🚀 .env 없음 (배포 환경으로 간주)")

import openai

# OPENAI_API_KEY 환경변수 설정 확인
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_tts(text, voice, output_dir):
    print(f"🌀 generate_tts() 호출됨: voice={voice}, text길이={len(text)}")
    output_path = os.path.join(output_dir, "audio.mp3")
    try:
        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text
        )
        with open(output_path, "wb") as f:
            f.write(response.content)
        print("✅ TTS 생성 성공")
        return output_path
    except Exception as e:
        print(f"❌ TTS 생성 실패: {e}")
        raise
