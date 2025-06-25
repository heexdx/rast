#!/usr/bin/env python3
"""
YouTube Video to PDF Frame Extractor - Improved Version
One large image per page, full width display

Requirements:
pip install yt-dlp opencv-python pillow reportlab

Usage:
python youtube_frame_extractor_improved.py
"""

import os
import cv2
import yt_dlp
from PIL import Image
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import tempfile
import shutil
from datetime import datetime

class YouTubeFrameExtractor:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.temp_dir = tempfile.mkdtemp()
        self.create_output_dir()
    
    def create_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def download_video(self, url, quality='best'):
        """Download YouTube video using yt-dlp"""
        try:
            ydl_opts = {
                'format': f'{quality}[ext=mp4]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                video_duration = info.get('duration', 0)
                
                print(f"Video: {video_title}")
                print(f"Duration: {video_duration} seconds")
                
                # Download video
                print("Downloading video...")
                ydl.download([url])
                
                # Find downloaded file
                for file in os.listdir(self.temp_dir):
                    if file.endswith('.mp4'):
                        video_path = os.path.join(self.temp_dir, file)
                        return video_path, video_title, video_duration
                
                raise Exception("Video file not found after download")
                
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None, None, None
    
    def extract_frames(self, video_path, interval_seconds=30, max_frames=50):
        """Extract frames from video at specified intervals"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            print(f"Video FPS: {fps}")
            print(f"Total frames: {total_frames}")
            print(f"Duration: {duration:.2f} seconds")
            
            frames = []
            frame_interval = int(fps * interval_seconds)
            frame_count = 0
            extracted_count = 0
            
            print(f"Extracting frames every {interval_seconds} seconds...")
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Extract frame at specified intervals
                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    
                    frames.append({
                        'image': pil_image,
                        'timestamp': timestamp,
                        'frame_number': frame_count
                    })
                    
                    extracted_count += 1
                    print(f"Extracted frame {extracted_count} at {timestamp:.2f}s")
                
                frame_count += 1
            
            cap.release()
            print(f"Total frames extracted: {len(frames)}")
            return frames
            
        except Exception as e:
            print(f"Error extracting frames: {str(e)}")
            return []
    
    def create_pdf(self, frames, video_title, output_filename=None):
        """Create PDF with one large image per page"""
        try:
            if not frames:
                print("No frames to create PDF")
                return None
            
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f"{safe_title}_{timestamp}_frames.pdf"
            
            pdf_path = os.path.join(self.output_dir, output_filename)
            
            # Create PDF document with A4 size
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize= landscape(A4),
                rightMargin=30,  # Smaller margins for larger images
                leftMargin=30,
                topMargin=50,
                bottomMargin=36
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                alignment=TA_CENTER,
                fontSize=16,
                spaceAfter=20
            )
            
            timestamp_style = ParagraphStyle(
                'CustomTimestamp',
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=14,
                textColor='blue',
                spaceAfter=10
            )
            
           
            # Calculate available space for images
            page_width, page_height = landscape(A4)
            available_width = page_width - 72  # Subtract margins
            available_height = page_height - 150  # Subtract margins and space for text
            
            # Add frames - one per page
            for i, frame_data in enumerate(frames):
                # Save frame as temporary image
                temp_img_path = os.path.join(self.temp_dir, f"frame_{i}.jpg")
                frame_data['image'].save(temp_img_path, 'JPEG', quality=95)
                
                # Add timestamp at top of page
                timestamp_text = f"Frame {i+1} - Time: {frame_data['timestamp']:.2f} seconds"
                timestamp = Paragraph(f"<b>{timestamp_text}</b>", timestamp_style)
                story.append(timestamp)
                story.append(Spacer(1, 10))
                
                # Add image - full width
                img = RLImage(temp_img_path)
                
                # Get original image dimensions
                img_width, img_height = frame_data['image'].size
                
                # Calculate scaling to fit width while maintaining aspect ratio
                width_scale = available_width / img_width
                height_scale = available_height / img_height
                scale = min(width_scale, height_scale)
                
                # Set image dimensions
                img.drawWidth = img_width * scale
                img.drawHeight = img_height * scale
                
                story.append(img)
                
                # Add page break except for last frame
                if i < len(frames) - 1:
                    story.append(PageBreak())
            
            # Build PDF
            print(f"Creating PDF: {pdf_path}")
            doc.build(story)
            
            print(f"PDF created successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"Error creating PDF: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")
    
    def extract_video_frames_to_pdf(self, youtube_url, interval_seconds=30, max_frames=50, quality='best'):
        """Main method to extract frames from YouTube video and create PDF"""
        try:
            print(f"Starting frame extraction for: {youtube_url}")
            
            # Download video
            video_path, video_title, duration = self.download_video(youtube_url, quality)
            if not video_path:
                return None
            
            # Extract frames
            frames = self.extract_frames(video_path, interval_seconds, max_frames)
            if not frames:
                return None
            
            # Create PDF
            pdf_path = self.create_pdf(frames, video_title)
            
            return pdf_path
            
        except Exception as e:
            print(f"Error in main extraction process: {str(e)}")
            return None
        finally:
            self.cleanup()

def main():
    """Interactive main function"""
    print("YouTube Video to PDF Frame Extractor - Improved Version")
    print("One large image per page")
    print("=" * 50)
    
    # Get user input
    youtube_url = input("Enter YouTube URL: ").strip()
    
    if not youtube_url:
        print("Please enter a valid YouTube URL")
        return
    
    try:
        interval = int(input("Frame extraction interval (seconds) [default: 30]: ") or "30")
        max_frames = int(input("Maximum frames to extract [default: 20]: ") or "20")
        
        quality_options = {
            '1': 'best',
            '2': 'worst', 
            '3': '720p',
            '4': '480p'
        }
        
        print("\nQuality options:")
        print("1. Best quality")
        print("2. Lowest quality (fastest)")
        print("3. 720p")
        print("4. 480p")
        
        quality_choice = input("Select quality [default: 1]: ").strip() or "1"
        quality = quality_options.get(quality_choice, 'best')
        
    except ValueError:
        print("Invalid input. Using default values.")
        interval = 30
        max_frames = 20
        quality = 'best'
    
    # Create extractor and process video
    extractor = YouTubeFrameExtractor()
    
    print(f"\nExtracting frames every {interval} seconds (max {max_frames} frames)...")
    print("Each frame will be displayed as a large image on its own page.")
    
    pdf_path = extractor.extract_video_frames_to_pdf(
        youtube_url, 
        interval_seconds=interval,
        max_frames=max_frames,
        quality=quality
    )
    
    if pdf_path:
        print(f"\n✅ Success! PDF created: {pdf_path}")
        print("Each frame is now displayed as a large image on its own page!")
    else:
        print("\n❌ Failed to create PDF")

if __name__ == "__main__":
    main()
