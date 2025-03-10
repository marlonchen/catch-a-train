#!/bin/bash
export DIRECTION_API_BASE_URL=https://router.project-osrm.org/route/v1/foot/
uvicorn --app-dir ../../src train_catcher.handler.restapi:app --reload