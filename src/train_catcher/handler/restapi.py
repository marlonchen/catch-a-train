from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

from train_catcher.adaptor.dist_cache import the_cache
from train_catcher.service.persistence import TimeoutException
from train_catcher.service.station_finder import StationFinder

app = FastAPI()

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
        station = finder.find_nearest_station(lat, lon)
        return station
    except TimeoutException:
        raise HTTPException(status_code=429, detail="Location search in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
