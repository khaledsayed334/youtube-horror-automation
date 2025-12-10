import os
import pickle
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


class YouTubeUploader:
    """Handles YouTube video uploads using OAuth2 credentials from environment variables."""
    
    def __init__(self):
        """Initialize YouTube API client with credentials from env vars."""
        self.credentials = self._load_credentials()
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def _load_credentials(self):
        """Build OAuth2 credentials from environment variables."""
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
        token_uri = os.getenv('YOUTUBE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
        scopes = os.getenv('YOUTUBE_SCOPES', 'https://www.googleapis.com/auth/youtube.upload').split()
        
        if not all([client_id, client_secret, refresh_token]):
            raise ValueError("Missing required YouTube OAuth credentials in environment variables")
        
        # Create credentials object
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes
        )
        
        # Refresh to get access token
        if creds.expired or not creds.token:
            creds.refresh(Request())
        
        return creds
    
    def upload_video(self, video_path, title, description, tags=None, category_id='24', 
                     privacy_status='public', thumbnail_path=None):
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags (optional)
            category_id: YouTube category ID (default: '24' = Entertainment)
            privacy_status: 'public', 'private', or 'unlisted' (default: 'public')
            thumbnail_path: Path to thumbnail image (optional)
        
        Returns:
            dict: Upload response with video ID and URL
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Prepare request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,  # Upload in a single request
            resumable=True,
            mimetype='video/*'
        )
        
        # Execute upload
        print(f"Uploading video: {title}")
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"Upload successful! Video ID: {video_id}")
        print(f"Video URL: {video_url}")
        
        # Upload thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path):
            self._upload_thumbnail(video_id, thumbnail_path)
        
        return {
            'video_id': video_id,
            'video_url': video_url,
            'title': title,
            'status': 'success'
        }
    
    def _upload_thumbnail(self, video_id, thumbnail_path):
        """Upload a custom thumbnail for a video."""
        try:
            print(f"Uploading thumbnail for video {video_id}")
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded successfully")
        except Exception as e:
            print(f"Warning: Failed to upload thumbnail: {e}")
    
    def get_channel_info(self):
        """Get information about the authenticated channel."""
        request = self.youtube.channels().list(
            part='snippet,statistics',
            mine=True
        )
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            return {
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'subscribers': channel['statistics'].get('subscriberCount', 'Hidden'),
                'video_count': channel['statistics']['videoCount'],
                'view_count': channel['statistics']['viewCount']
            }
        return None


# Test function
if __name__ == '__main__':
    # Test credentials loading
    try:
        uploader = YouTubeUploader()
        print("✓ YouTube credentials loaded successfully")
        
        # Get channel info
        info = uploader.get_channel_info()
        if info:
            print(f"✓ Connected to channel: {info['title']}")
            print(f"  - Videos: {info['video_count']}")
            print(f"  - Views: {info['view_count']}")
    except Exception as e:
        print(f"✗ Error: {e}")
