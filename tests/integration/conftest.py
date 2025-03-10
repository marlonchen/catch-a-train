import os

import pytest
from fastapi.testclient import TestClient

from train_catcher.handler.restapi import app

os.environ['REDIS_HOST'] = 'localhost'
os.environ['DIRECTION_API_BASE_URL'] = 'https://api.openstreetmap.org/directions/v2/walking/'  # https://router.project-osrm.org/route/v1/foot/
os.environ['SEPTA_TRAIN_SCHEDULE_URL'] = 'https://www3.septa.org/api/Arrivals/index.php'

client = TestClient(app)

@pytest.fixture(scope='session')
def api_client():
    return client
@pytest.fixture
def api_base_url() -> str:
    return 'http://localhost:8000'


@pytest.fixture
def headers() -> dict:
    return {'X-API-Key': '123'}
