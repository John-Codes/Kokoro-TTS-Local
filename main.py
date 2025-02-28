from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import asyncio

app = FastAPI()
semaphore = asyncio.Semaphore(1)  # Single execution at a time

class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0

async def run_tts(text: str, speed: float):
    try:
        # Build command to output to stdout using '-' convention
        command = [
            "python", "kokoro_cli.py",
            "--voice", "af_bella",
            "--text", text,
            "--speed", str(speed),
            "--output", "-"  # Tell CLI to output to stdout
        ]

        # Launch process
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Read stdout stream
        mp3_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=30)

        # Check for errors
        if proc.returncode != 0:
            stderr = (await proc.stderr.read()).decode()
            raise RuntimeError(f"TTS failed: {stderr}")

        return mp3_bytes

    except Exception as e:
        raise RuntimeError(f"TTS error: {str(e)}") from e

@app.post("/generate-speech/")
async def generate_speech(request: TTSRequest):
    async with semaphore:  # Ensure single execution
        try:
            mp3_bytes = await run_tts(request.text, request.speed)
            
            if not mp3_bytes:
                raise HTTPException(500, "Empty audio response")
                
            return Response(
                content=mp3_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment; filename=speech.mp3"}
            )
            
        except Exception as e:
            raise HTTPException(500, detail=str(e))