from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.state import session_manager
from app.interview_engine import process_interview_turn

app = FastAPI()

class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

@app.post("/api/interview")
async def handle_interview(req: InterviewRequest):
    if not req.sessionId:
        raise HTTPException(status_code=400, detail="sessionId is required.")

    session = session_manager.get_or_create(req.sessionId, req.candidate)

    try:
        if req.message is None and req.candidate is not None:
            result = process_interview_turn(session, user_message=None)
        elif req.message is not None:
            result = process_interview_turn(session, user_message=req.message)
        else:
            raise HTTPException(status_code=400, detail="Provide 'candidate' or 'message'.")

        return result
    except Exception as e:
        # Catch any error and show exact message in browser
        return {
            "reply": f"Backend Error: {str(e)}",
            "done": False
        }