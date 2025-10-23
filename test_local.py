#!/usr/bin/env python3
"""
Local testing script to verify the main.py setup and predict functions work correctly.
This script simulates the Cerebrium environment without actually deploying.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import Item, setup, predict


class MockContext:
    pass


def test_setup():
    """Test that setup runs without errors."""
    print("Testing setup()...")
    try:
        setup()
        print("✓ Setup completed successfully!")
        return True
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return False


def test_predict():
    """Test prediction with sample inputs."""
    print("\nTesting predict()...")
    
    test_item = Item(
        video_url="https://github.com/anotherjesse/LatentSync/raw/main/assets/yuxin.mp4",
        audio_url="https://github.com/anotherjesse/LatentSync/raw/main/assets/audio_yuxin.wav",
        guidance_scale=1.5,
        inference_steps=20,
        seed=1247
    )
    
    try:
        context = MockContext()
        result = predict(test_item, context)
        
        if "video_base64" in result and result["video_base64"]:
            print("✓ Predict completed successfully!")
            print(f"  Output video size: {len(result['video_base64'])} bytes (base64)")
            return True
        else:
            print("✗ Predict failed: No video_base64 in result")
            return False
    except Exception as e:
        print(f"✗ Predict failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LatentSync Cerebrium Deployment - Local Test")
    print("=" * 60)
    
    setup_ok = test_setup()
    
    if setup_ok:
        print("\n" + "=" * 60)
        predict_ok = test_predict()
        print("=" * 60)
        
        if predict_ok:
            print("\n✓ All tests passed! Deployment should work correctly.")
            sys.exit(0)
        else:
            print("\n✗ Prediction test failed. Please check the logs above.")
            sys.exit(1)
    else:
        print("\n✗ Setup test failed. Cannot proceed with prediction test.")
        sys.exit(1)
