# Monitoring Dashboard

A small system and Docker monitoring dashboard built with **Python, Flask, Docker, Docker Compose, and GitHub Actions**.

The project monitors the host system and Docker containers, exposes the information through a Flask dashboard, records logs, and uses GitHub Actions to automatically test the application and its Docker setup.

---

## Features

* Monitor system resource usage.
* Monitor Docker containers and their states.
* Count running and stopped containers.
* Display monitoring information through a Flask web dashboard.
* Expose monitoring data through a JSON API.
* Automatically refresh dashboard data.
* Record Docker activity in log files.
* Record alerts in a separate log file.
* Run the monitoring program in a finite CI mode.
* Dockerize the monitoring application.
* Run the application using Docker Compose.
* Automatically test the project with GitHub Actions.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │   Monitoring App     │
                    │      Python         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
       System monitoring                  Docker monitoring
              │                                 │
              └────────────────┬────────────────┘
                               │
                               ▼
                         Flask server
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
                 Dashboard              API
                 HTML/UI           /api/dashboard
```

The application can also be packaged as a Docker image:

```text
Python application
       │
       ▼
   Dockerfile
       │
       ▼
 Docker image
       │
       ▼
 Docker container
       │
       ▼
 Flask dashboard
```

---

# Flask Web Server

The project uses Flask to expose the monitoring information through a web interface.

The main route:

```text
GET /
```

renders the dashboard.

The dashboard receives information such as:

* system usage
* Docker containers
* number of running containers
* number of stopped containers
* current time

---

## API

The project also exposes:

```text
GET /api/dashboard
```

which returns monitoring information as JSON.

Example structure:

```json
{
  "system": {},
  "docker": {},
  "running": 0,
  "stopped": 0,
  "time": "..."
}
```

This separates the monitoring data from the HTML presentation.

---

# Dashboard Refresh

The dashboard uses JavaScript to periodically request the server.

The basic idea is:

```text
Browser
   │
   │ HTTP request
   ▼
Flask /
   │
   ▼
HTML
   │
   ▼
Browser updates dashboard
```

The refresh interval is currently a few seconds.

Instead of replacing the entire HTML document, the JavaScript can parse the returned HTML and replace the relevant dashboard content.

---

# Static JavaScript

Flask does not automatically serve arbitrary files from any directory on the filesystem.

A route was therefore added for the JavaScript file:

```text
/js/<filename>
```

The browser requests:

```text
GET /js/fetching.js
```

and Flask serves the file from the project's JavaScript directory.

This also helped clarify an important web-server concept:

```text
Browser request
      ↓
Flask route
      ↓
filesystem
      ↓
file response
```

The browser does not directly access the server's filesystem.

---

# Logging

The application writes monitoring information and alerts to separate log files:

```text
setup/
└── logs/
    ├── docker.log
    └── alerts.log
```

The Docker monitoring information is written to:

```text
docker.log
```

while alert-related events are written to:

```text
alerts.log
```

The logs can be inspected with:

```bash
cat ./setup/logs/docker.log
cat ./setup/logs/alerts.log
```

The application uses normal file-based logging. Log rotation with `RotatingFileHandler` is **not currently implemented**.

---

# Discord Alerts

The monitoring application can send alerts to Discord when a monitored Docker container changes state.

The application sends an HTTP `POST` request to a Discord webhook.

The general flow is:

```text
Docker monitoring
       ↓
container state changes
       ↓
alert generated
       ↓
HTTP POST request
       ↓
Discord webhook
       ↓
Discord channel
```

The request contains a JSON payload representing the alert.

Conceptually:

```http
POST <Discord Webhook>
Content-Type: application/json
```

with a payload similar to:

```json
{
  "content": "Docker container state changed"
}
```

The Discord webhook URL is kept outside the source code rather than being committed directly to the repository.

The application also keeps track of the previous container state so that it can distinguish between:

```text
container was already stopped
```

and:

```text
container changed from running → stopped
```

This prevents the monitoring loop from repeatedly sending the same alert every few seconds.

The alert flow is therefore:

```text
Current Docker state
        +
Previous Docker state
        ↓
   State changed?
      /       \
    NO         YES
    ↓           ↓
nothing      write alert
                ↓
          send Discord POST
```

---

# Configuration

Configuration is stored separately from the application code.

```text
setup/
└── conf/
    └── usage.conf
```

The configuration can be inspected with:

```bash
cat ./setup/conf/usage.conf
```

---

# Docker

The application is containerized using a `Dockerfile`.

The basic Docker workflow is:

```text
Dockerfile
    │
    ▼
docker build
    │
    ▼
Docker image
    │
    ▼
docker run
    │
    ▼
Container
```

The image is built with:

```bash
docker build -t monitor .
```

and can be started with:

```bash
docker run -d --name AserverHC -p 5000:5000 monitor
```

The port mapping exposes the Flask server running inside the container to the host:

```text
Host :5000
   │
   ▼
Container :5000
   │
   ▼
Flask
```

---

# Docker Compose

The project also contains a Docker Compose configuration.

Compose is used to describe how the application should be run as a service instead of manually specifying every Docker option.

Typical commands:

```bash
docker compose build
```

```bash
docker compose up
```

```bash
docker compose down
```

The project also tested running the service directly in CI with:

```bash
docker compose run AserverHc --ci
```

---

# CI Mode

The monitoring application normally contains an endless monitoring loop.

That is appropriate for a real monitoring application, but it is a problem in automated testing.

Therefore, the application has a `--ci` mode.

Normal execution:

```bash
python ./setup/script.py
```

```text
start
  ↓
monitor
  ↓
monitor
  ↓
monitor
  ↓
...
```

CI execution:

```bash
python ./setup/script.py --ci
```

```text
start
  ↓
monitor
  ↓
monitor
  ↓
limited iterations
  ↓
exit
```

This allows GitHub Actions to run the application without waiting forever.

---

# GitHub Actions

The project contains a GitHub Actions workflow:

```text
.github/
└── workflows/
    └── monitoring_wk.yml
```

The workflow is triggered by pushes to the repository.

The current pipeline contains three chained jobs:

```text
push
 │
 ▼
Job ONE
 │
 ▼
Job TWO
 │
 ▼
Job THREE
```

Each job uses:

```yaml
runs-on: ubuntu-latest
```

which gives the job a temporary GitHub-hosted Ubuntu runner.

---

# CI Job ONE — Python

The first job checks that the Python application can run.

It performs:

```text
checkout repository
        ↓
setup Python 3.12
        ↓
install dependencies
        ↓
inspect configuration
        ↓
run monitoring application in --ci mode
        ↓
inspect logs
```

The important command is:

```bash
python ./setup/script.py --ci
```

If the program exits with a non-zero exit status, GitHub Actions considers the step failed.

---

# CI Job TWO — Docker

The second job tests the Docker image.

It:

```text
checkout repository
        ↓
docker build
        ↓
docker run
        ↓
wait
        ↓
curl Flask endpoint
        ↓
remove container
```

The Docker image is built using:

```bash
docker build -t monitor .
```

The container is started in detached mode:

```bash
docker run -d --name AserverHC -p 5000:5000 monitor --ci
```

The `-d` option allows the container to run in the background while the GitHub Actions runner continues executing commands.

The Flask server can then be tested with:

```bash
curl http://localhost:5000
```

---

# CI Job THREE — Docker Compose

The third job tests the Compose configuration.

It:

```text
checkout repository
        ↓
docker compose build
        ↓
docker compose run
        ↓
application starts
```

This verifies that the project can also be built and executed through Docker Compose.

---

# Job Dependencies

The jobs use GitHub Actions `needs`:

```yaml
two:
  needs: one
```

and:

```yaml
three:
  needs: two
```

Therefore:

```text
ONE
 │
 │ success
 ▼
TWO
 │
 │ success
 ▼
THREE
```

If an earlier job fails, the next dependent job does not run.

---

# Cleanup

Containers created during CI should be removed after testing.

For example:

```bash
docker rm -f AserverHC
```

GitHub Actions can run cleanup even when an earlier step fails:

```yaml
if: always()
```

For example:

```yaml
- name: cleanup
  if: always()
  run: docker rm -f AserverHC
```

This is useful because a failed test should not prevent cleanup.

---

# CI vs CD

The project currently focuses primarily on **CI**.

The implemented pipeline verifies:

```text
Python works
     ↓
Docker build works
     ↓
Docker container works
     ↓
Flask responds
     ↓
Docker Compose works
```

Actual deployment is not currently implemented.

A future CD architecture could be:

```text
Git push
   ↓
GitHub Actions
   ↓
CI tests
   ↓
Docker image
   ↓
Docker registry
   ↓
Deployment server
   ↓
docker pull
   ↓
docker compose up
```

This is intentionally left as a future phase.

---

# What I Learned

This project was used to understand several concepts together:

### Python

* process execution
* configuration files
* logging
* monitoring
* finite CI execution

### Flask

* routes
* templates
* JSON APIs
* serving files
* HTTP requests
* development server lifecycle

### JavaScript

* `fetch()`
* asynchronous requests
* promises
* `DOMParser`
* updating existing DOM content
* periodic refresh with `setInterval()`

### Docker

* Dockerfiles
* images
* containers
* port mapping
* detached containers
* volumes
* Docker Compose

### CI/CD

* GitHub Actions
* workflows
* jobs
* steps
* runners
* `needs`
* exit codes
* cleanup
* `if: always()`
* CI testing
* difference between CI and actual deployment

---

# Current Status

## Completed

* [x] Python monitoring application
* [x] Docker monitoring
* [x] Flask dashboard
* [x] JSON API
* [x] Dashboard auto-refresh
* [x] Logging
* [x] Dockerfile
* [x] Docker Compose configuration
* [x] CI mode
* [x] GitHub Actions workflow
* [x] Python CI testing
* [x] Docker CI testing
* [x] Docker Compose CI testing
* [x] Flask HTTP health check
* [x] Container cleanup

## Future Improvements

* [ ] Improve dashboard design
* [ ] Add more monitoring features
* [ ] Improve alerting
* [ ] Better HTTP health checks
* [ ] Docker image versioning
* [ ] Push images to a container registry
* [ ] Deploy to a persistent server
* [ ] Implement full CD
* [ ] Add automated deployment
* [ ] Add deployment rollback

---

## Main Goal

The goal of this project was not simply to make a monitoring dashboard.

It was to understand the complete path:

```text
Application
    ↓
Web server
    ↓
Docker
    ↓
Docker Compose
    ↓
Git
    ↓
GitHub Actions
    ↓
Automated testing
```

The project currently stops at automated CI testing. Deployment/CD is left for a later phase.
