#!/usr/bin/env python3
"""
Test inference script for Wan2.2 TI2V model on Cerebrium
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v"
API_KEY = os.getenv("CEREBRIUM_API_KEY")

def test_t2v_inference():
    """Test pure Text-to-Video generation"""
    print("\n" + "="*60)
    print("Testing Text-to-Video (T2V) Generation")
    print("="*60)
    
    payload = {
        "prompt": "A beautiful sunset over a calm ocean with birds flying in formation",
        "negative_prompt": "low quality, blurry, distorted, artifact",
        "height": 704,
        "width": 1280,
        "num_frames": 121,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "fps": 24,
        "seed": 42
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\nEndpoint: {API_BASE_URL}/predict")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers=headers,
            timeout=600
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Inference successful!")
            
            # Check if video_base64 is in result
            if "video_base64" in result:
                video_base64 = result["video_base64"]
                # Save video
                video_path = Path("/tmp/test_output_t2v.mp4")
                video_bytes = base64.b64decode(video_base64)
                video_path.write_bytes(video_bytes)
                print(f"✅ Video saved to: {video_path}")
                print(f"   Video size: {len(video_bytes) / 1024 / 1024:.2f} MB")
            
            # Print details
            if "details" in result:
                print("\nGeneration Details:")
                for key, value in result["details"].items():
                    print(f"  - {key}: {value}")
        else:
            print("❌ Request failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out (inference took longer than 10 minutes)")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ti2v_inference():
    """Test Text-Image-to-Video generation"""
    print("\n" + "="*60)
    print("Testing Text-Image-to-Video (TI2V) Generation")
    print("="*60)
    
    # Create a simple test image or use URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Metal_texture.jpg/1200px-Metal_texture.jpg"
    
    payload = {
        "prompt": "A person dancing gracefully to music",
        "negative_prompt": "low quality, blurry",
        "height": 704,
        "width": 1280,
        "num_frames": 121,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "fps": 24,
        "image_url": image_url,
        "seed": 123
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\nEndpoint: {API_BASE_URL}/predict")
    print(f"Using reference image from URL")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers=headers,
            timeout=600
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Inference successful!")
            
            # Check if video_base64 is in result
            if "video_base64" in result:
                video_base64 = result["video_base64"]
                # Save video
                video_path = Path("/tmp/test_output_ti2v.mp4")
                video_bytes = base64.b64decode(video_base64)
                video_path.write_bytes(video_bytes)
                print(f"✅ Video saved to: {video_path}")
                print(f"   Video size: {len(video_bytes) / 1024 / 1024:.2f} MB")
            
            # Print details
            if "details" in result:
                print("\nGeneration Details:")
                for key, value in result["details"].items():
                    print(f"  - {key}: {value}")
        else:
            print("❌ Request failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out (inference took longer than 10 minutes)")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if not API_KEY:
        print("❌ Error: CEREBRIUM_API_KEY environment variable not set")
        print("Please set your API key: export CEREBRIUM_API_KEY='your-key'")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Wan2.2 TI2V Model - Inference Test")
    print("="*60)
    print(f"Project ID: p-194bc83f")
    print(f"API Base: {API_BASE_URL}")
    
    # Test T2V
    test_t2v_inference()
    
    # Test TI2V (comment out if you want to skip)
    # test_ti2v_inference()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
