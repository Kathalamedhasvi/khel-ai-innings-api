from fastapi import FastAPI, HTTPException, status
from app.schemas import InningsSummaryRequest, InningsSummaryResponse
from app.services import InningsCalculatorService

app = FastAPI(
    title="Khel AI - Innings Summary API",
    description="Integration-Ready API to calculate full innings summaries from raw ball-by-ball event data.",
    version="2.0.0"
)

@app.get("/")
def health_check():
    return {"status": "online", "system": "Khel AI MVP"}

@app.post(
    "/api/v1/innings/summary",
    response_model=InningsSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute Innings Summary"
)
def get_innings_summary(payload: InningsSummaryRequest):
    """
    Accepts raw ball-event log data and computes statistics dynamically.
    No hardcoded summaries are used.
    """
    try:
        summary = InningsCalculatorService.calculate_summary(payload)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process ball events: {str(e)}"
        )