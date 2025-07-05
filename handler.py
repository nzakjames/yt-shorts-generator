import os, uuid, shutil
from app.tts import generate_tts
from app.whisper_wrapper import transcribe_audio
from app.sad_talker_wrapper import generate_talking_video
from app.video_finalizer import combine_video_audio_subtitles
from app.utils import download_image
from app.utils import download_models

import base64
from google.cloud import storage
from datetime import timedelta


print("✅ handler.py 시작됨")




def handler(event):
    print("📥 handler() 진입")
    print("📦 입력 이벤트:", event)

    # ✅ 헬스체크 또는 잘못된 요청인 경우 무시하고 종료
    if not event or event == {} or "input" not in event:
        print("💤 헬스체크 요청 감지됨 또는 input 누락 → 종료")
        return {"status": "ok (healthcheck)"}



    try:
        # ✅ 모델 다운로드 (이미 다운로드된 경우 생략됨)
        download_models()

        inputs = event.get("input", {})
        if not isinstance(inputs, dict):
            raise ValueError("input 필드가 dict 타입이 아닙니다.")

        text = inputs.get("text")
        image_url = inputs.get("image_url")
        voice = inputs.get("voice", "nova")

        if not text or not image_url:
            raise ValueError("text와 image_url은 필수 입력값입니다.")

        session_id = str(uuid.uuid4())
        work_dir = f"/tmp/{session_id}"
        os.makedirs(work_dir, exist_ok=True)
        print(f"📁 작업 디렉토리 생성: {work_dir}")

        # 1. 이미지 다운로드
        image_path = download_image(image_url, work_dir)
        print(f"🖼️ 이미지 다운로드 완료: {image_path}")

        # 2. TTS 음성 생성
        audio_path = generate_tts(text, voice, work_dir)
        print(f"🔊 TTS 생성 완료: {audio_path}")

        # 3. 자막 생성
        subtitle_path = transcribe_audio(audio_path, work_dir)
        print(f"💬 자막 생성 완료: {subtitle_path}")

        ### 로컬 테스트에서는 제외
        # 4. 얼굴 영상 생성 (SadTalker)
        video_path = generate_talking_video(image_path, audio_path, work_dir)
        print(f"🎥 영상 생성 완료: {video_path}")

        # local test용
        # video_path = "/Users/james/Documents/Python/yt-shorts-generator/test_assets/test_video_35.mp4"


        # 5. 자막 입혀서 최종 영상 합성
        final_video_path = combine_video_audio_subtitles(video_path, audio_path, subtitle_path, work_dir)
        print(f"✅ 최종 영상 생성 완료: {final_video_path}")



        #### 6. GCS 업로드 및 Signed URL 생성
        # 1. 환경변수에서 base64 읽기
        gcs_key_b64 = os.environ.get("GCS_KEY_B64")
        if not gcs_key_b64:
            raise RuntimeError("환경변수 GCS_KEY_B64가 설정되지 않았습니다.")

        # 2. base64 decode하여 임시 파일로 저장
        gcs_key_path = "/tmp/gcs-key.json"
        with open(gcs_key_path, "wb") as f:
            f.write(base64.b64decode(gcs_key_b64))

        # 3. GCS 클라이언트 생성
        client = storage.Client.from_service_account_json(gcs_key_path)

        # 4. 업로드 대상 버킷 및 경로 설정
        bucket = client.bucket("my-video-bucket-202507")  # ← 실제 버킷명 입력
        object_name = f"runpod_outputs/{session_id}.mp4"  # 원하는 경로/이름
        blob = bucket.blob(object_name)

        # 5. 영상 파일 업로드
        blob.upload_from_filename(final_video_path)
        print(f"✅ GCS 업로드 완료: gs://{bucket.name}/{object_name}")

        # 6. Signed URL 생성
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET"
        )
        print("🔗 Signed URL:", signed_url)

        # 7. 응답 반환
        return {
            "video_url": signed_url
        }




    except Exception as e:
        print(f"❌ 예외 발생: {type(e).__name__}: {str(e)}")
        return {"error": str(e)}



### test시
# if __name__ == "__main__":
#     test_event = {
#         "input": {
#             "text": "족저근막염은 발바닥의 두꺼운 섬유 띠인 족저근막에 염증이 생겨 통증을 유발하는 상태로, 특히 운동 후 통증이 심해질 수 있습니다. 운동 후 족저근막염 통증을 완화하기 위한 방법들을 자세히 설명해 드리겠습니다. 1. 휴식 및 활동 조절 운동 후 족저근막에 과도한 부담이 가지 않도록 충분히 휴식을 취하는 것이 중요합니다. 통증이 있을 때는 특히 장시간 서 있거나 걷는 것을 피하고, 운동 강도나 시간을 줄여서 염증을 악화시키지 않도록 조절해야 합니다. ",
#             "image_url": "https://raw.githubusercontent.com/OpenTalker/SadTalker/main/examples/source_image/full_body_1.png",
#             "voice": "alloy"
#         }
#     }
#     result = handler(test_event)
#     print("🎬 최종 결과:", result)        
