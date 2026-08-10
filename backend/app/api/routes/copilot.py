from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CopilotRequest(BaseModel):
    question: str

class CopilotResponse(BaseModel):
    answer: str
    sources: list

@router.post("/copilot", response_model=CopilotResponse)
def ask_copilot(req: CopilotRequest):
    # RAG pattern placeholder
    # Question -> Knowledge Base -> Decision Engine -> ML Results -> Business Rules -> LLM
    
    # Mocking keyword-based response for prototype
    keyword = req.question.lower()
    if "risk" in keyword:
        return {
            "answer": "The main risk factor currently is a supplier delay for WIDGET-B due to geopolitical issues.",
            "sources": ["Risk Engine", "Knowledge Graph"]
        }
    return {
        "answer": "I have analyzed your request across our AI models and supply chain graph. The data suggests maintaining current safety stock levels.",
        "sources": ["Decision Engine"]
    }
