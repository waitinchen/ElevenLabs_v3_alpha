"""FastAPI WebSocket endpoint for streaming audio to Whisper."""

import os
import tempfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from openai import OpenAI


router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
CHUNK_THRESHOLD = 4  # number of MediaRecorder chunks (~2-4 seconds)

client: OpenAI | None = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)


async def _transcribe_chunks(chunks: List[bytes]) -> str:
    """Persist chunks to a temp file and call Whisper transcription."""
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
        for chunk in chunks:
            tmp_file.write(chunk)
        temp_path = Path(tmp_file.name)

    try:
        with temp_path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
            )
        return response.text or ""
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


@router.websocket("/api/whisper")
async def whisper_websocket(websocket: WebSocket):
    await websocket.accept()

    if not client:
        await websocket.send_json(
            {
                "type": "error",
                "message": "OPENAI_API_KEY 未設定，無法使用 Whisper 服務",
            }
        )
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    audio_chunks: List[bytes] = []

    try:
        await websocket.send_json({"type": "ready"})

        while True:
            message = await websocket.receive()

            if "bytes" in message and message["bytes"] is not None:
                audio_chunks.append(message["bytes"])

                if len(audio_chunks) >= CHUNK_THRESHOLD:
                    try:
                        text = await _transcribe_chunks(audio_chunks)
                        await websocket.send_json({"type": "final", "text": text})
                    except Exception as exc:  # noqa: BLE001
                        await websocket.send_json({"type": "error", "message": str(exc)})
                    finally:
                        audio_chunks.clear()

            elif message.get("type") == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        pass
    finally:
        if audio_chunks:
            try:
                text = await _transcribe_chunks(audio_chunks)
                await websocket.send_json({"type": "final", "text": text})
            except Exception:
                pass
        audio_chunks.clear()

