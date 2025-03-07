#!/bin/bash
export DIRECTION_API_ROOT=https://router.project-osrm.org/route/v1/foot/
uvicorn --app-dir ../../src train_catcher.handler.restapi:app --reload