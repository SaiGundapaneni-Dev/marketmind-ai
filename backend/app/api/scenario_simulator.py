from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.core.database import get_db
from app.schemas.scenario_simulator_schema import (
    ScenarioPresetsResponse,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
)
from app.services.scenario_simulator_service import (
    ScenarioSimulatorService,
)


router = APIRouter(
    prefix="/portfolio/scenarios",
    tags=["Scenario Simulator"],
)


@router.get(
    "/presets",
    response_model=ScenarioPresetsResponse,
)
def get_scenario_presets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        ScenarioSimulatorService.list_presets(
            db,
            current_user.id,
        )
    )


@router.post(
    "/simulate",
    response_model=ScenarioSimulationResponse,
)
def simulate_scenario(
    payload: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ScenarioSimulatorService.simulate(
        db=db,
        user_id=current_user.id,
        scenario_name=payload.name,
        changes=payload.changes,
    )
