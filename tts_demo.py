# test_api.py
import requests
import time

API_URL = "http://localhost:8000/generate-speech/"
TEST_TEXT = "Hello world! This is a test of the Kokoro TTS API."
OUTPUT_FILE = f"test_output_{int(time.time())}.mp3"

def test_tts_api():
    try:
        # Get available voices first
        voices_response = requests.get("http://localhost:8000/voices")
        voices = voices_response.json()['voices']
        print(f"Available voices: {voices}")

        # Test parameters
        payload = {
            "text": TEST_TEXT,
            "speed": 1.2,
            "voice": voices[0] if voices else "af_bella"
        }

        # Make the request
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            with open(OUTPUT_FILE, "wb") as f:
                f.write(response.content)
            print(f"Success! Audio saved to {OUTPUT_FILE}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Kokoro TTS API")
    if test_tts_api():
        print("Test succeeded!")
    else:
        print("Test failed!")