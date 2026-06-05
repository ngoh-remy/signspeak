from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
import os
import sys

# Ensure current directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inference import recognizer

app = FastAPI(
    title="SignSpeak Inference Service",
    description="Standalone real-time sign language prediction microservice for Hugging Face Spaces."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Inference service starting up...")
    recognizer.load()
    print("Inference model loaded successfully.")

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "SignSpeak Inference Service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/recognize")
async def websocket_recognize(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    recognizer.reset()

    await websocket.send_json({
        "type": "connected",
        "message": "SignSpeak inference engine ready.",
        "session_id": session_id,
    })

    try:
        while True:
            # Receive video frame bytes from the React client
            frame_bytes = await websocket.receive_bytes()
            
            # Process the frame through the LSTM + MediaPipe pipeline
            result = recognizer.process_frame(frame_bytes)

            if result is not None:
                sign_label, confidence = result
                await websocket.send_json({
                    "type": "recognition",
                    "sign": sign_label,
                    "confidence": round(confidence, 4),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            else:
                # Accumulating frames to build the sequence of 30
                frames_buffered = len(recognizer.sequence_buffer)
                await websocket.send_json({
                    "type": "processing",
                    "frames_buffered": frames_buffered,
                    "frames_needed": 30,
                })
    except WebSocketDisconnect:
        print(f"WebSocket disconnected (session: {session_id})")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Inference engine error: {str(e)}",
            })
        except Exception:
            pass
