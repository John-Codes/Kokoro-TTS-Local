import requests
import time

# Configuration
API_URL = "http://localhost:8000/generate-speech/"
TEST_TEXT = "I am a filfthy fat cat who loves to eat fish all day long."
SPEED = 1.2  # Test speed (0.5-2.0)
OUTPUT_FILE = f"test_output_{int(time.time())}.mp3"  # Unique filename with timestamp

def test_tts_api():
    try:
        # Create the request payload
        payload = {
            "text": TEST_TEXT,
            "speed": SPEED
        }

        # Make the POST request
        response = requests.post(API_URL, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the MP3 bytes to file
            with open(OUTPUT_FILE, "wb") as f:
                f.write(response.content)
            print(f"Success! Audio saved to {OUTPUT_FILE}")
            print(f"Response headers: {response.headers}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Testing TTS API with:")
    print(f"Text: {TEST_TEXT}")
    print(f"Speed: {SPEED}x")
    print(f"API URL: {API_URL}")
    
    success = test_tts_api()
    
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")