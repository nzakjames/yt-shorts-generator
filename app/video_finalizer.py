import subprocess
import os
import shlex

def combine_video_audio_subtitles(video_path, audio_path, subtitle_path, output_dir):
    final_path = os.path.join(output_dir, "final_video.mp4")

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"영상 파일이 존재하지 않습니다: {video_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"오디오 파일이 존재하지 않습니다: {audio_path}")
    if not os.path.isfile(subtitle_path):
        raise FileNotFoundError(f"자막 파일이 존재하지 않습니다: {subtitle_path}")

    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-vf", f"subtitles={shlex.quote(subtitle_path)}:force_style='FontName=NanumGothic,Fontsize=32,Alignment=2',scale=720:720,pad=720:1280:0:280",
            "-c:v", "libx264", "-c:a", "aac",
            final_path
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg 실행 실패:\n{e.stderr}")

    if not os.path.isfile(final_path):
        raise FileNotFoundError("최종 영상 파일이 생성되지 않았습니다.")

    return final_path
