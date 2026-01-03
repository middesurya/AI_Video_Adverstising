"""
Video Generation Service
Handles actual video generation using various APIs
"""
import os
import requests
import time
from typing import List, Dict
import json

class VideoGenerationService:
    """Service for generating videos using cloud APIs"""
    
    def __init__(self):
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.runway_api_key = os.getenv("RUNWAY_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.use_mock = os.getenv("USE_MOCK_VIDEO", "true").lower() == "true"
        
    
    def generate_video_for_scene(self, scene: Dict, ad_brief: Dict, output_dir: str) -> str:
        """
        Generate video for a single scene
        
        Args:
            scene: Scene dictionary with description, duration, etc.
            ad_brief: Ad brief dictionary with product info
            output_dir: Directory to save the video
            
        Returns:
            Path to generated video file (relative to backend root)
        """
        
        if self.use_mock or not (self.stability_api_key or self.runway_api_key):
            # Return mock video path
            filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene-{scene.get('description', 'scene')[:20].replace(' ', '-')}.mp4"
            return f"/videos/{filename}"
        
        # Try Runway ML first (more reliable for video)
        if self.runway_api_key:
            return self._generate_with_runway(scene, ad_brief, output_dir)
        
        # Fallback to Stability AI (may not work for video)
        if self.stability_api_key:
            return self._generate_with_stability(scene, ad_brief, output_dir)
        
        # Default to mock
        filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene.mp4"
        return f"/videos/{filename}"
    
    def _generate_with_stability(self, scene: Dict, ad_brief: Dict, output_dir: str) -> str:
        """Generate video using Stability AI API (image-to-video)"""
        
        try:
            # Step 1: Generate an image from text prompt
            image_prompt = f"{scene.get('description', '')}. Style: {ad_brief.get('style', 'cinematic')}, professional, high quality"
            
            
            print(f"Generating image for scene: {image_prompt}")
            
            # Generate image using Stability AI image generation
            image_response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/core",
                headers={
                    "Authorization": f"Bearer {self.stability_api_key}",
                    "Accept": "application/json"
                },
                files={
                    "none": ""
                },
                data={
                    "prompt": image_prompt,
                    "output_format": "png",
                    "aspect_ratio": "16:9"
                },
                timeout=60
            )
            
            
            if image_response.status_code != 200:
                error_msg = image_response.text
                print(f"Stability AI image generation failed: {error_msg}")
                raise Exception(f"Image generation failed: {error_msg}")
            
            # Parse image response
            image_data = image_response.json()
            
            
            if "image" not in image_data:
                raise Exception("No image in response")
            
            # Save image temporarily
            import base64
            image_bytes = base64.b64decode(image_data["image"])
            temp_image_path = os.path.join(output_dir, f"temp-image-{int(time.time())}.png")
            with open(temp_image_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"Image generated, saved to: {temp_image_path}")
            
            
            # Step 2: Convert image to video using Stable Video Diffusion
            print("Converting image to video...")
            
            # Try v2beta endpoint first (more stable)
            endpoint_version = "v2beta"
            video_response = requests.post(
                f"https://api.stability.ai/{endpoint_version}/generation/image-to-video",
                headers={
                    "Authorization": f"Bearer {self.stability_api_key}",
                    "Accept": "application/json"
                },
                files={
                    "image": (os.path.basename(temp_image_path), open(temp_image_path, 'rb'), 'image/png')
                },
                data={
                    "seed": 0,
                    "cfg_scale": 1.8,
                    "motion_bucket_id": 127
                },
                timeout=120
            )
            
            
            # If v2beta fails, try v1alpha (alternative endpoint)
            if video_response.status_code == 404:
                
                endpoint_version = "v1alpha"
                video_response = requests.post(
                    f"https://api.stability.ai/{endpoint_version}/generation/image-to-video",
                    headers={
                        "Authorization": f"Bearer {self.stability_api_key}",
                        "Accept": "application/json"
                    },
                    files={
                        "image": (os.path.basename(temp_image_path), open(temp_image_path, 'rb'), 'image/png')
                    },
                    data={
                        "seed": 0,
                        "cfg_scale": 1.8,
                        "motion_bucket_id": 127
                    },
                    timeout=120
                )
            
            # Clean up temp image
            try:
                os.remove(temp_image_path)
            except:
                pass
            
            
            if video_response.status_code not in [200, 202]:
                error_msg = video_response.text
                print(f"Stability AI video generation failed: {error_msg}")
                
                
                # Note: Stability AI video generation API may not be publicly available
                # For now, create a placeholder video file so the frontend can display something
                # In production, you'd want to use Runway ML or another service
                raise Exception(f"Video generation failed (Status {video_response.status_code}): {error_msg}. Note: Stability AI video generation may require a different API endpoint or service.")
            
            # Handle async response (202) or sync response (200)
            if video_response.status_code == 202:
                # Async generation - poll for result
                generation_id = video_response.json().get("id")
                
                
                if not generation_id:
                    raise Exception("No generation ID in response")
                
                print(f"Video generation started, ID: {generation_id}")
                print("Polling for completion...")
                
                # Poll for completion
                max_polls = 60  # 5 minutes max
                poll_interval = 5  # 5 seconds
                
                for i in range(max_polls):
                    time.sleep(poll_interval)
                    # Use same version as the initial request (endpoint_version is set above)
                    status_response = requests.get(
                        f"https://api.stability.ai/{endpoint_version}/generation/image-to-video/result/{generation_id}",
                        headers={
                            "Authorization": f"Bearer {self.stability_api_key}",
                            "Accept": "video/*"
                        },
                        timeout=30
                    )
                    
                    
                    if status_response.status_code == 200:
                        # Video ready
                        video_bytes = status_response.content
                        break
                    elif status_response.status_code == 202:
                        # Still processing
                        print(f"Still processing... ({i+1}/{max_polls})")
                        continue
                    else:
                        raise Exception(f"Status check failed: {status_response.text}")
                else:
                    raise Exception("Video generation timed out")
            else:
                # Sync response - video ready immediately
                video_bytes = video_response.content
                
            
            # Save video
            filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene-{int(time.time())}.mp4"
            output_path = os.path.join(output_dir, filename)
            
            
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
            
            
            print(f"Video generated successfully: {output_path}")
            return f"/videos/{filename}"
            
        except Exception as e:
            print(f"Stability AI error: {e}")
            import traceback
            traceback.print_exc()
            
            
            # Fallback to mock
            filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene.mp4"
            
            
            return f"/videos/{filename}"
    
    def _generate_with_runway(self, scene: Dict, ad_brief: Dict, output_dir: str) -> str:
        """Generate video using Runway ML API"""
        
        try:
            # Runway ML text-to-video generation
            prompt = f"{scene.get('description', '')}. Style: {ad_brief.get('style', 'cinematic')}, professional, high quality"
            duration = min(scene.get('duration', 10), 10)  # Max 10 seconds for Runway ML
            
            
            print(f"Generating video with Runway ML: {prompt}")
            
            # Runway ML API endpoint for text-to-video (Gen-4 Turbo)
            # Correct endpoint: api.dev.runwayml.com (not api.runwayml.com)
            runway_response = requests.post(
                "https://api.dev.runwayml.com/v1/tasks/text-to-video",
                headers={
                    "Authorization": f"Bearer {self.runway_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gen4_turbo",
                    "promptText": prompt,
                    "ratio": "1920:1080",  # 16:9 aspect ratio
                    "duration": duration
                },
                timeout=120
            )
            
            
            if runway_response.status_code not in [200, 201, 202]:
                error_msg = runway_response.text
                print(f"Runway ML API error: {error_msg}")
                raise Exception(f"Runway ML API error (Status {runway_response.status_code}): {error_msg}")
            
            # Parse response
            task_data = runway_response.json()
            task_id = task_data.get("id") or task_data.get("task_id")
            
            if not task_id:
                raise Exception("No task ID in Runway ML response")
            
            print(f"Runway ML task created: {task_id}")
            print("Polling for completion...")
            
            
            # Poll for task completion
            max_polls = 60  # 5 minutes max
            poll_interval = 5  # 5 seconds
            
            for i in range(max_polls):
                time.sleep(poll_interval)
                
                status_response = requests.get(
                    f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.runway_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                
                
                if status_response.status_code != 200:
                    raise Exception(f"Status check failed: {status_response.text}")
                
                task_status = status_response.json()
                status = task_status.get("status")
                
                if status == "completed" or status == "succeeded":
                    # Video ready
                    output = task_status.get("output") or task_status.get("result")
                    if isinstance(output, list) and len(output) > 0:
                        video_url = output[0].get("url") if isinstance(output[0], dict) else output[0]
                    elif isinstance(output, dict):
                        video_url = output.get("url") or output.get("video_url")
                    else:
                        video_url = output
                    
                    if not video_url:
                        raise Exception("No video URL in completed task")
                    
                    
                    print(f"Video ready, downloading from: {video_url}")
                    break
                elif status == "failed" or status == "error":
                    error_msg = task_status.get("error") or task_status.get("message") or "Unknown error"
                    raise Exception(f"Runway ML task failed: {error_msg}")
                else:
                    # Still processing
                    print(f"Still processing... ({i+1}/{max_polls}) - Status: {status}")
                    continue
            else:
                raise Exception("Runway ML video generation timed out")
            
            # Download video from URL
            print("Downloading video...")
            video_download = requests.get(video_url, timeout=120)
            
            if video_download.status_code != 200:
                raise Exception(f"Failed to download video: {video_download.status_code}")
            
            # Save video
            filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene-{int(time.time())}.mp4"
            output_path = os.path.join(output_dir, filename)
            
            
            with open(output_path, 'wb') as f:
                f.write(video_download.content)
            
            
            print(f"Video generated successfully: {output_path}")
            return f"/videos/{filename}"
            
        except Exception as e:
            print(f"Runway ML error: {e}")
            import traceback
            traceback.print_exc()
            
            
            # Fallback to mock
            filename = f"{ad_brief.get('productName', 'product').lower().replace(' ', '-')}-scene.mp4"
            return f"/videos/{filename}"
    
    def generate_audio_for_scene(self, scene: Dict, output_dir: str) -> str:
        """Generate TTS audio for a scene"""
        narration = scene.get('narration', scene.get('description', ''))
        
        if not narration:
            return None
        
        # Use ElevenLabs if available
        if self.elevenlabs_api_key:
            return self._generate_with_elevenlabs(narration, scene, output_dir)
        
        # For now, return None (no audio)
        return None
    
    def _generate_with_elevenlabs(self, text: str, scene: Dict, output_dir: str) -> str:
        """Generate audio using ElevenLabs API"""
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default voice
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                filename = f"audio-{scene.get('description', 'scene')[:20].replace(' ', '-')}.mp3"
                output_path = os.path.join(output_dir, filename)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            
            return None
            
        except Exception as e:
            print(f"ElevenLabs error: {e}")
            return None
    
    def combine_video_and_audio(self, video_path: str, audio_path: str, output_path: str):
        """Combine video and audio using FFmpeg"""
        try:
            import ffmpeg
            
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            
            ffmpeg.output(
                video, audio,
                output_path,
                vcodec='copy',
                acodec='aac',
                shortest=None
            ).overwrite_output().run()
            
        except ImportError:
            print("ffmpeg-python not installed. Install with: pip install ffmpeg-python")
            # Just copy video if no audio
            import shutil
            shutil.copy(video_path, output_path)
        except Exception as e:
            print(f"FFmpeg error: {e}")
            # Fallback: just copy video
            import shutil
            shutil.copy(video_path, output_path)

