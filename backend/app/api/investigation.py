from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.investigation import InvestigationRequest, InvestigationResponse
from app.services.investigation_agent import FraudInvestigationAgent, investigation_agent
from app.core.logging import logger

router = APIRouter(prefix="/investigation", tags=["Fraud Investigation Agent"])


def get_investigation_agent() -> FraudInvestigationAgent:
    return investigation_agent


@router.post("/analyze", response_model=InvestigationResponse, status_code=status.HTTP_200_OK)
async def analyze_case_graph_evidence(
    request: InvestigationRequest,
    agent: FraudInvestigationAgent = Depends(get_investigation_agent),
) -> InvestigationResponse:
    """
    Execute 12-step graph evidence investigation for a target ClosedCase vertex ID.
    Returns structured evidence, risk patterns, rule evaluations, and reasoning.
    """
    try:
        logger.info(f"Received investigation request for case_id: {request.case_id}")
        response = agent.investigate(request)
        return response
    except Exception as e:
        logger.error(f"Error during graph evidence investigation for {request.case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation execution failed: {str(e)}",
        )
