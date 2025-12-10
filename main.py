# main.py
import time
from datetime import datetime

from youtube_uploader import YouTubeUploader
from video_pipeline import generate_main_video, generate_short_from_main

# 288 minutes = 4.8 hours
INTERVAL_MINUTES = 288


def run_automation_cycle():
    uploader = YouTubeUploader()

    # 1) Main horror video
    main_data = generate_main_video()
    main_upload = uploader.upload_video(
        video_path=main_data["video_path"],
        title=main_data["title"],
        description=main_data["description"],
        tags=main_data.get("tags", []),
        privacy_status="public",
    )
    print("Main video upload result:", main_upload)

    # 2) Short (based on main video)
    short_data = generate_short_from_main(main_data["video_path"])
    short_upload = uploader.upload_video(
        video_path=short_data["video_path"],
        title=short_data["title"],
        description=short_data["description"],
        tags=short_data.get("tags", []),
        privacy_status="public",
    )
    print("Short upload result:", short_upload)


def main_loop():
    print("Starting 24/7 automation loop on Render...")
    while True:
        print(f"[{datetime.utcnow()}] Starting cycle")
        try:
            run_automation_cycle()
            print(f"[{datetime.utcnow()}] Cycle finished successfully")
        except Exception as e:
            print(f"[{datetime.utcnow()}] Cycle FAILED: {e}")
        # Wait until next run
        print(f"Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main_loop()

