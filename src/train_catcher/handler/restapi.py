from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Response, Security
from fastapi.security import APIKeyHeader
from prometheus_client import generate_latest

from train_catcher.adaptor.cache_store import the_cache
from train_catcher.service.plan_notif_scheduler import PlanNotificationScheduler
from train_catcher.service.time_to_leave import TimeToLeavePlanner
from train_catcher.service.notifier import Notifier
from train_catcher.service.persistence import TimeoutException
from train_catcher.service.station_finder import (
    METRICS_REG,
    NotWithinServiceAreaException,
    StationFinder,
)

app = FastAPI()

# Metrics endpoint for Prometheus
@app.get('/metrics')
def get_metrics():
    return Response(
        media_type='text/plain',
        content=generate_latest(METRICS_REG)
    )


# Authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def _is_valid_api_key(api_key: str) -> bool:
    """
    Validate API key against Redis store.
    Returns True if key is valid, False otherwise.
    """
    # Check if key exists and is not rate limited
    key_data = the_cache().get(f"apikey:{api_key}")
    
    if not key_data:
        return False
    
    # Check if key is enabled
    return key_data == 'enabled'

def _verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not _is_valid_api_key(api_key):
        raise HTTPException(status_code=403)
    return api_key

@app.get("/nearest_station")
async def find_nearest_station(
    lat: float,
    lon: float,
    phone: Optional[str] = None,
    api_key: str = Depends(_verify_api_key)
):
    try:
        finder = StationFinder()
        direction = finder.find_nearest_station(lat, lon)
        notifier = Notifier(phone)
        notifier.send_walking_direction(direction)
        return direction
    except NotWithinServiceAreaException:
        raise HTTPException(status_code=400, detail="Location is outside service area")
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/time_to_leave")
async def get_time_to_leave(
    lat: float,
    lon: float,
    line: str,
    direction: str,
    phone: Optional[str] = None,
    api_key: str = Depends(_verify_api_key)
):
    try:
        planner = TimeToLeavePlanner()
        plan = planner.plan_time_to_leave(lat, lon, line, direction)
        scheduler = PlanNotificationScheduler(phone)
        scheduler.schedule(plan)
        return plan
    except NotWithinServiceAreaException:
        raise HTTPException(status_code=400, detail="Location is outside service area")
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
