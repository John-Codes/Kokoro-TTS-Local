# main.py
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import asyncio
import torch
import soundfile as sf
from io import BytesIO
import numpy as np
from models import build_model, list_available_voices

print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else "N/A"}')
print(f'cuDNN version: {torch.backends.cudnn.version() if torch.cuda.is_available() else "N/A"}')
print(f'Device count: {torch.cuda.device_count()}')
print(f'Current device: {torch.cuda.current_device()}')
print(f'Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"}')

app = FastAPI()
semaphore = asyncio.Semaphore(1)  # Single execution at a time

# Model configuration
MODEL_PATH = 'kokoro-v1_0.pth'
SAMPLE_RATE = 24000
DEFAULT_VOICE = "af_bella"

# Initialize model once at startup
@app.on_event("startup")
async def load_model():
    try:
        app.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing model on {app.device}...")
        app.model = build_model(MODEL_PATH, app.device)
        app.voices = list_available_voices()
        print("Model loaded successfully")
    except Exception as e:
        raise RuntimeError(f"Model initialization failed: {str(e)}")

class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    voice: str = DEFAULT_VOICE

def generate_audio(text: str, voice: str, speed: float) -> bytes:
    try:
        # Validate voice selection
        if voice not in app.voices:
            raise ValueError(f"Invalid voice '{voice}'. Available voices: {app.voices}")
        
        # Generate speech
        all_audio = []
        generator = app.model(
            text, 
            voice=f"voices/{voice}.pt", 
            speed=speed, 
            split_pattern=r'\n+'
        )

        for gs, ps, audio in generator:
            if audio is not None:
                if isinstance(audio, np.ndarray):
                    audio = torch.from_numpy(audio).float()
                all_audio.append(audio)

        if not all_audio:
            raise ValueError("No audio generated")

        # Combine and convert to bytes
        final_audio = torch.cat(all_audio, dim=0).numpy()
        
        # Convert to MP3 bytes
        with BytesIO() as buffer:
            sf.write(buffer, final_audio, SAMPLE_RATE, format='mp3')
            return buffer.getvalue()

    except Exception as e:
        raise RuntimeError(f"Generation failed: {str(e)}")

@app.post("/generate-speech/")
async def generate_speech(request: TTSRequest):
    async with semaphore:
        try:
            # Validate input
            if not request.text.strip():
                raise ValueError("Text cannot be empty")
            
            if not 0.5 <= request.speed <= 2.0:
                raise ValueError("Speed must be between 0.5 and 2.0")

            # Generate audio
            mp3_bytes = generate_audio(
                request.text,
                request.voice,
                request.speed
            )

            return Response(
                content=mp3_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"attachment; filename=speech.mp3"}
            )

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/voices")
async def list_voices():
    return {"voices": app.voices}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)