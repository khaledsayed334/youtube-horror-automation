import os
import json
import subprocess
import random
from pathlib import Path
from openai import OpenAI
from datetime import datetime


class VideoPipeline:
    """Advanced horror video generation pipeline using OpenAI + FFmpeg."""
    
    def __init__(self, output_dir='outputs'):
        """Initialize the video pipeline."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / 'audio').mkdir(exist_ok=True)
        (self.output_dir / 'videos').mkdir(exist_ok=True)
        (self.output_dir / 'thumbnails').mkdir(exist_ok=True)
    
    def generate_horror_script(self, video_type='main', duration_minutes=3):
        """
        Generate a horror script using OpenAI.
        
        Args:
            video_type: 'main' (2-5 min) or 'short' (1 min)
            duration_minutes: Target duration in minutes
        
        Returns:
            dict: Script data with title, narration, description, tags
        """
        if video_type == 'short':
            prompt = """Generate a short 60-second horror story perfect for YouTube Shorts.

Requirements:
- Hook in first 3 seconds
- One terrifying scene or twist
- Cliffhanger ending
- Narration: 150-180 words
- Title must be attention-grabbing with numbers or questions
- Include 5 relevant hashtags

Format your response as JSON:
{
  "title": "string",
  "narration": "string",
  "description": "string",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}"""
        else:
            word_count = duration_minutes * 150  # ~150 words per minute
            prompt = f"""Generate a {duration_minutes}-minute horror story for YouTube.

Requirements:
- Compelling hook in first 15 seconds
- Build tension gradually
- Satisfying climax and resolution
- Narration: {word_count}-{word_count + 50} words
- Title with keywords for SEO (include "TRUE", "REAL", year, or location)
- Include 10 relevant tags

Popular themes: urban legends, true crime, paranormal, creepypasta, scary stories

Format your response as JSON:
{{
  "title": "string",
  "narration": "string",
  "description": "string",
  "tags": ["tag1", "tag2", ..., "tag10"]
}}"""
        
        print(f"Generating {video_type} horror script...")
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional horror content writer for YouTube. Create engaging, scary stories that keep viewers hooked."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.9
        )
        
        script_data = json.loads(response.choices[0].message.content)
        print(f"✓ Script generated: {script_data['title']}")
        return script_data
    
    def generate_audio(self, text, filename):
        """
        Generate audio narration using OpenAI TTS.
        
        Args:
            text: Script text to convert to speech
            filename: Output filename (without extension)
        
        Returns:
            Path: Path to generated audio file
        """
        audio_path = self.output_dir / 'audio' / f'{filename}.mp3'
        
        print(f"Generating audio narration...")
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="onyx",  # Deep, dramatic voice perfect for horror
            input=text,
            speed=0.95  # Slightly slower for dramatic effect
        )
        
        response.stream_to_file(str(audio_path))
        print(f"✓ Audio saved: {audio_path}")
        return audio_path
    
    def create_video_with_ffmpeg(self, audio_path, video_type='main', filename='output'):
        """
        Create video using FFmpeg with audio + visual effects.
        
        Args:
            audio_path: Path to audio file
            video_type: 'main' or 'short' (affects resolution)
            filename: Output filename
        
        Returns:
            Path: Path to generated video file
        """
        video_path = self.output_dir / 'videos' / f'{filename}.mp4'
        
        # Get audio duration
        duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        
        # Set resolution based on video type
        if video_type == 'short':
            width, height = 1080, 1920  # Vertical for Shorts
        else:
            width, height = 1920, 1080  # Horizontal for main videos
        
        print(f"Creating {video_type} video with FFmpeg...")
        
        # Create atmospheric horror video with animated gradient background
        # and pulsing text overlay effect
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            # Generate animated dark gradient background
            '-f', 'lavfi', '-i', f'color=c=0x0a0a0a:s={width}x{height}:d={duration}',
            # Add noise overlay for grain effect
            '-f', 'lavfi', '-i', f'noise=c0s=10:allf=t:s={width}x{height}:d={duration}',
            # Audio input
            '-i', str(audio_path),
            # Complex filter for visual effects
            '-filter_complex',
            f'[0:v][1:v]blend=all_mode=overlay:all_opacity=0.3[bg];'
            f'[bg]fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1[v]',
            # Video codec settings
            '-map', '[v]', '-map', '2:a',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart',
            str(video_path)
        ]
        
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"✓ Video created: {video_path}")
        return video_path
    
    def generate_thumbnail(self, title, filename):
        """
        Generate a thumbnail image using DALL-E.
        
        Args:
            title: Video title
            filename: Output filename
        
        Returns:
            Path: Path to thumbnail file
        """
        thumbnail_path = self.output_dir / 'thumbnails' / f'{filename}.png'
        
        print("Generating thumbnail with DALL-E...")
        prompt = f"Create a dark, eerie horror thumbnail for YouTube. Theme: {title}. Style: cinematic, dramatic lighting, red and black colors, mysterious atmosphere, high contrast"
        
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",  # YouTube thumbnail aspect ratio
            quality="standard",
            n=1
        )
        
        # Download and save thumbnail
        import urllib.request
        urllib.request.urlretrieve(response.data[0].url, str(thumbnail_path))
        print(f"✓ Thumbnail saved: {thumbnail_path}")
        return thumbnail_path
    
    def create_complete_video(self, video_type='main', duration_minutes=3):
        """
        Generate complete video: script → audio → video → thumbnail.
        
        Args:
            video_type: 'main' or 'short'
            duration_minutes: Target duration
        
        Returns:
            dict: Complete video data with paths and metadata
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f'{video_type}_{timestamp}'
        
        # Step 1: Generate script
        script = self.generate_horror_script(video_type, duration_minutes)
        
        # Step 2: Generate audio
        audio_path = self.generate_audio(script['narration'], base_filename)
        
        # Step 3: Create video
        video_path = self.create_video_with_ffmpeg(audio_path, video_type, base_filename)
        
        # Step 4: Generate thumbnail
        thumbnail_path = self.generate_thumbnail(script['title'], base_filename)
        
        return {
            'video_path': str(video_path),
            'thumbnail_path': str(thumbnail_path),
            'audio_path': str(audio_path),
            'title': script['title'],
            'description': script['description'],
            'tags': script['tags'],
            'video_type': video_type,
            'timestamp': timestamp
        }


# Test function
if __name__ == '__main__':
    pipeline = VideoPipeline()
    
    # Test script generation
    print("\n=== Testing Script Generation ===")
    script = pipeline.generate_horror_script('main', 2)
    print(f"Title: {script['title']}")
    print(f"Tags: {', '.join(script['tags'])}")
    print(f"Narration length: {len(script['narration'])} characters")
