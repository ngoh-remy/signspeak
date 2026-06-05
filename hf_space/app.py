from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
import os
import sys
import asyncio

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

    # Reset MediaPipe holistic + frame buffer for a clean session.
    # Must run in a thread because holistic.close() + recreation does I/O.
    await asyncio.to_thread(recognizer.new_session)

    await websocket.send_json({
        "type": "connected",
        "message": "SignSpeak inference engine ready.",
        "session_id": session_id,
    })

    # Lock prevents concurrent MediaPipe calls; drops frames when busy.
    lock = asyncio.Lock()

    try:
        from inference import SIMULATION_MODE, SIMULATION_REASON
        print(f"[*] Connection received. Active Engine Status: {'SIMULATION' if SIMULATION_MODE else 'REAL-INFERENCE'} (Reason: {SIMULATION_REASON})")
        
        while True:
            frame_bytes = await websocket.receive_bytes()
            
            # Drop frames if inference is still running to prevent backpressure.
            if lock.locked():
                continue
                
            async with lock:
                result = await asyncio.to_thread(recognizer.process_frame, frame_bytes)

            if result is not None:
                sign_label, confidence = result
                await websocket.send_json({
                    "type": "recognition",
                    "sign": sign_label,
                    "confidence": round(confidence, 4),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            else:
                frames_buffered = len(recognizer.sequence_buffer)
                await websocket.send_json({
                    "type": "processing",
                    "frames_buffered": frames_buffered,
                    "frames_needed": 20,
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
    finally:
        # Pre-warm holistic for the next connection attempt so reconnects are instant.
        # This runs AFTER the connection closes, in a background thread.
        asyncio.create_task(asyncio.to_thread(recognizer.new_session))
        print(f"[+] Session {session_id} cleaned up. Holistic pre-warmed for next connection.")

