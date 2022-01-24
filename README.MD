# Asgi application provided by FastAPI

![test_workflow](https://github.com/GLEF1X/fastapi-project/actions/workflows/mypy_and_tests.yaml/badge.svg)

**If you want to check how to implement pure "clean architecture", you can visit another [github repo](https://github.com/GLEF1X/blacksheep-clean-architecture)**

### What has already been done?🧭

- Deployment using Docker and docker-compose
- Deployment using kubernetes(with backups by cron, volumes for database)
- Tests for API routes and JWT helper funcs using pytest
- Integration with `github actions` to provide automatic execution of tests and mypy lint


### TODO:

- Make own small dependency injector
- Finish up OAuth2 authorization
- Make tests for all routes and endpoints
- Provide Docker & Docker-compose compability with CD
