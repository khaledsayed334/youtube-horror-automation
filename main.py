import os
import random
from datetime import datetime
from video_pipeline import VideoPipeline
from youtube_uploader import YouTubeUploader


def run_automation_cycle():
    """
    Main automation cycle: Generate video → Upload to YouTube.
    
    Returns:
        dict: Result with status, video_url, title, etc.
    """
    print("\n" + "="*60)
    print("YOUTUBE HORROR AUTOMATION CYCLE")
    print("="*60)
    
    try:
        # Initialize components
        pipeline = VideoPipeline(output_dir='outputs')
        uploader = YouTubeUploader()
        
        # Decide video type: 70% main videos, 30% shorts
        video_type = 'main' if random.random() < 0.7 else 'short'
        
        # Set duration based on type
        if video_type == 'main':
            duration = random.randint(2, 5)  # 2-5 minutes
        else:
            duration = 1  # 1 minute for shorts
        
        print(f"\n📹 Video Type: {video_type.upper()}")
        print(f"⏱️  Duration: {duration} minute(s)")
        
        # Step 1: Generate complete video with script, audio, video, thumbnail
        print("\n[1/2] Generating video content...")
        video_data = pipeline.create_complete_video(
            video_type=video_type,
            duration_minutes=duration
        )
        
        print(f"✓ Video generated: {video_data['title']}")
        print(f"  - Video file: {video_data['video_path']}")
        print(f"  - Thumbnail: {video_data['thumbnail_path']}")
        print(f"  - Tags: {', '.join(video_data['tags'][:5])}...")
        
        # Step 2: Upload to YouTube
        print("\n[2/2] Uploading to YouTube...")
        upload_result = uploader.upload_video(
            video_path=video_data['video_path'],
            title=video_data['title'],
            description=video_data['description'],
            tags=video_data['tags'],
            category_id='24',  # Entertainment
            privacy_status='public',
            thumbnail_path=video_data['thumbnail_path']
        )
        
        print(f"\n{'='*60}")
        print("✅ AUTOMATION CYCLE COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"🎬 Video: {upload_result['title']}")
        print(f"🔗 URL: {upload_result['video_url']}")
        print(f"📊 Type: {video_type}")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"{'='*60}\n")
        
        return {
            'status': 'success',
            'video_id': upload_result['video_id'],
            'video_url': upload_result['video_url'],
            'title': upload_result['title'],
            'video_type': video_type,
            'duration_minutes': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"\n{'='*60}")
        print("❌ AUTOMATION CYCLE FAILED")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# For local testing
if __name__ == '__main__':
    print("Running single automation cycle for testing...")
    result = run_automation_cycle()
    
    if result['status'] == 'success':
        print(f"\n✓ Test successful!")
        print(f"Video URL: {result['video_url']}")
    else:
        print(f"\n✗ Test failed: {result.get('error', 'Unknown error')}")
