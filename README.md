# catch-a-train

## How to run tests

1. Create a codespace from github

1. Run the following command if virtual environment is not automatically activated
```
python -m venv venv
./venv/bin/activate
```

1. Install dependencies
```
pip install .
```

1. Start external dependencies in docker environment
```
docker compose down && docker compose up --build -d
```

1. Run tests
```
pytest
```

## How to start the server

1. Start the server via command line - navigate in the file explorer to folder `tests/cli`, right click and select "Open in Integrated Terminal", and then in the new terminal, run,
```
./run.sh
```

1. Repeat last step to start another terminal, and run,
```
./test.sh
```

## How to debug API

1. Use unit tests or integration tests to test logic

1. To test API layer, use VS Code's "FastAPI" configuration in debug panel.

1. Run `./test.sh` in terminal at folder `tests/cli`
