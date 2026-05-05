# Cloud Task Manager

**Author:** Joseph Nweke  
**Course:** CSC 468 — Introduction to Cloud Computing  
**Repository:** CloudLab-ready containerized web application

---

## Table of Contents

1. [Vision](#vision)
2. [Proposal](#proposal)
3. [Build Process](#build-process)
4. [Networking](#networking)
5. [Deployment on CloudLab](#deployment-on-cloudlab)
6. [System Design](#system-design)
7. [Demo & Testing](#demo--testing)

---

## Vision

### What This System Does

The Cloud Task Manager is a two-tier, containerized web application that allows users to manage personal tasks through a browser. Users can:

- **Create** tasks by entering a title and optional description
- **View** all current tasks along with their completion status
- **Complete** tasks by toggling their status from pending to done
- **Undo** completed tasks back to pending
- **Delete** tasks that are no longer needed

The infrastructure manages the full lifecycle of a task record: creation, retrieval, state mutation (mark complete/incomplete), and deletion. All task state is held in memory within the backend container for the duration of the session.

### System Components

The application is divided into two independent services, each running in its own Docker container:

| Component | Role | Technology |
|---|---|---|
| **Frontend** | Renders the web UI; handles user interactions; calls the backend | Python / Flask / HTML |
| **Backend** | Exposes a REST API; stores and manages task data in memory | Python / Flask |

### Architecture Diagram

```
                        ┌─────────────────────────────────┐
                        │           CloudLab Node          │
                        │                                  │
  ┌────────┐            │  ┌──────────────────────────┐   │
  │        │  HTTP :5001 │  │  Frontend Container      │   │
  │  User  │ ──────────►│  │  (python:3.11-slim)      │   │
  │Browser │            │  │  Flask app on port 5001  │   │
  │        │◄────────── │  └──────────┬───────────────┘   │
  └────────┘  HTML Page │             │                    │
                        │      REST API (HTTP)             │
                        │      http://backend:5000         │
                        │             │                    │
                        │  ┌──────────▼───────────────┐   │
                        │  │  Backend Container        │   │
                        │  │  (python:3.11-slim)       │   │
                        │  │  Flask API on port 5000   │   │
                        │  │  In-memory task store     │   │
                        │  └──────────────────────────┘   │
                        │                                  │
                        │  [ tasknet — Docker bridge ]     │
                        └─────────────────────────────────┘
```

**Communication flow:**

1. The user's browser sends an HTTP request to the Frontend on port `5001`.
2. The Frontend Flask app processes the request and issues one or more REST API calls to the Backend on port `5000` over the internal Docker bridge network (`tasknet`).
3. The Backend processes the API call, updates the in-memory task store, and returns a JSON response.
4. The Frontend renders the response as an HTML page and returns it to the user's browser.

All frontend-to-backend communication happens entirely within the Docker network and is never exposed directly to the user.

---

## Proposal

### Base Images

Both services use `python:3.11-slim` as their base Docker image. This image was chosen for the following reasons:

- **Slim variant reduces image size.** The `slim` tag strips out non-essential OS packages (documentation, build tools, extra locales) while keeping Python fully functional. This results in a significantly smaller image compared to the full `python:3.11` image — important for fast deployment on CloudLab nodes.
- **Python 3.11 is the stable long-term release.** It offers improved error messages and better performance compared to earlier versions, and has broad compatibility with Flask 3.x and the `requests` library.
- **No Alpine is used here intentionally.** While `python:alpine` is even smaller, it uses `musl libc` instead of `glibc`, which can cause subtle compatibility issues with compiled Python packages. The `slim` variant avoids this tradeoff while still achieving a small footprint.

### Service Frameworks

| Service | Framework | Reason |
|---|---|---|
| Frontend | Flask 3.x + Jinja2 | Lightweight server-side rendering; no JavaScript build step required; easy to serve HTML templates from Python |
| Backend | Flask 3.x | Minimal, easy-to-read REST API; well-suited for in-memory data structures |

---

## Build Process

### Backend Dockerfile — Line by Line

```dockerfile
FROM python:3.11-slim
```
Selects the official Python 3.11 slim base image from Docker Hub. The `slim` variant is used because it removes unnecessary OS packages (man pages, build utilities) while keeping the Python interpreter intact. This keeps the final image size small and speeds up pulls on CloudLab.

```dockerfile
WORKDIR /app
```
Sets the working directory inside the container to `/app`. All subsequent `COPY`, `RUN`, and `CMD` instructions operate relative to this path. This is a best practice that keeps the container filesystem organized and prevents files from being scattered in the root directory.

```dockerfile
COPY requirements.txt .
```
Copies only the `requirements.txt` file first, before copying the rest of the application code. This is a deliberate Docker layer caching optimization: since dependencies rarely change, Docker can cache the `pip install` layer and skip it on future rebuilds when only the application code changes.

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
Installs the Python dependencies listed in `requirements.txt`. The `--no-cache-dir` flag tells pip not to store the downloaded packages in a local cache directory, which reduces the final image size since that cache would otherwise be included in the image layer.

```dockerfile
COPY . .
```
Copies the rest of the application source code (primarily `app.py`) into the `/app` directory in the container. This step comes after `pip install` to maximize cache reuse.

```dockerfile
EXPOSE 5000
```
Documents that the container listens on port `5000` at runtime. This is metadata only — it does not actually publish the port to the host. The actual port binding is handled in `docker-compose.yml`.

```dockerfile
CMD ["python", "-u", "app.py"]
```
Defines the default command to run when the container starts. The `-u` flag runs Python in unbuffered mode, which ensures that `print()` output and log messages are immediately flushed to stdout. This is important for seeing real-time logs with `docker compose logs`.

### Frontend Dockerfile — Line by Line

The Frontend Dockerfile follows the same structure as the Backend with two differences:

```dockerfile
EXPOSE 5001
```
The frontend runs on port `5001` to avoid a port conflict with the backend.

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
Installs both `flask` and `requests`. The `requests` library is needed because the frontend makes HTTP calls to the backend REST API from Python server-side code.

---

## Networking

### Docker Network: `tasknet`

Both containers are connected to a custom Docker bridge network named `tasknet`, defined explicitly in `docker-compose.yml`:

```yaml
networks:
  tasknet:
    driver: bridge
```

A custom named network is used instead of the default Compose network for two reasons:
1. It makes the network explicit and self-documenting.
2. It enables Docker's built-in DNS resolution between containers by name.

### DNS Resolution by Container Name

Docker Compose automatically registers each service's container name as a DNS hostname on the shared network. This means the frontend can reach the backend using the hostname `backend` — no IP address required:

```python
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:5000')
```

When the frontend calls `http://backend:5000/tasks`, Docker's internal DNS resolver looks up `backend` on the `tasknet` network and routes the request to the backend container's IP address automatically. This is robust to container restarts because the hostname always resolves to whichever container is currently running under that name.

### Port Mapping

| Service | Internal Port | Host Port | Access |
|---|---|---|---|
| Backend | 5000 | 5000 | `http://<node-ip>:5000` |
| Frontend | 5001 | 5001 | `http://<node-ip>:5001` |

The backend's host port is exposed for direct API testing (e.g., with `curl`). Normal users only interact with the frontend on port `5001`.

### Health Check

The backend service includes a Docker health check:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
  interval: 10s
  timeout: 5s
  retries: 3
```

The frontend is configured with `depends_on: condition: service_healthy`, which means Compose will not start the frontend until the backend has passed its health check. This prevents the frontend from crashing on startup because the backend is not yet ready to accept connections.

---

## Deployment on CloudLab

### Prerequisites

- A running CloudLab node (Ubuntu 22.04 recommended)
- SSH access to the node
- Git installed on the node

### Step-by-Step Deployment

**1. Reserve a CloudLab node**

Log in to CloudLab, create a new experiment, and provision a single Ubuntu 22.04 node. Wait for the node to reach the `Ready` state, then copy the SSH command.

**2. SSH into the node**

```bash
ssh <your-username>@<node-hostname>.cloudlab.us
```

**3. Clone the repository**

```bash
git clone https://github.com/<your-username>/cloud-task-manager.git
cd cloud-task-manager
```

**4. Run the setup script**

The included `setup.sh` script automates Docker installation and container deployment:

```bash
bash setup.sh
```

The script performs the following steps automatically:
- Updates system packages with `apt-get`
- Installs Docker Engine using the official Docker install script
- Installs Docker Compose plugin
- Builds both container images from the local Dockerfiles
- Starts both containers in detached mode

**5. Open the firewall (if needed)**

CloudLab nodes may block ports by default. Open ports `5000` and `5001` if you cannot reach the application:

```bash
sudo ufw allow 5000
sudo ufw allow 5001
```

**6. Access the application**

Open your browser and navigate to:

```
http://<cloudlab-node-public-ip>:5001
```

### Useful Commands

```bash
# View running containers
docker compose ps

# Stream live logs from both services
docker compose logs -f

# Stream logs from backend only
docker compose logs -f backend

# Stop all containers
docker compose down

# Rebuild and restart after code changes
docker compose up --build -d
```

### Manual Deployment (without setup.sh)

If you prefer to run steps manually:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get install -y docker-compose-plugin

# Build and start
docker compose up --build -d
```

---

## System Design

### REST API Reference

The backend exposes the following HTTP endpoints:

| Method | Endpoint | Description | Request Body | Response |
|---|---|---|---|---|
| `GET` | `/health` | Health check | — | `{"status": "ok"}` |
| `GET` | `/tasks` | Retrieve all tasks | — | Array of task objects |
| `POST` | `/tasks` | Create a new task | `{"title": "...", "description": "..."}` | Created task object |
| `PUT` | `/tasks/<id>` | Toggle task completion | `{}` | Updated task object |
| `DELETE` | `/tasks/<id>` | Delete a task | — | `{"message": "Task deleted"}` |

**Task object schema:**

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

### Design Decisions

**Why two separate containers instead of one?**  
Separating the frontend and backend enforces a clean separation of concerns. The backend is a stateless REST API that knows nothing about HTML rendering. The frontend is a presentation layer that knows nothing about data storage. This separation makes each service independently deployable, testable, and replaceable. If a different frontend (e.g., a React app or a mobile app) were needed in the future, the backend would require zero changes.

**Why Flask for both services?**  
Flask is a lightweight micro-framework that is easy to read and understand, making it ideal for a course project where code clarity matters. It has no required project structure, minimal boilerplate, and straightforward route definitions. For a small two-service application, Flask's simplicity outweighs the organizational benefits of a heavier framework like Django.

**Why in-memory storage?**  
A persistent database (e.g., PostgreSQL, SQLite) was intentionally omitted to keep the architecture focused on containerization and networking concepts. The trade-off is that task data is lost when the backend container restarts. Adding a database volume would be a natural next step to make the system production-ready.

**Why `python:3.11-slim` over `python:alpine`?**  
Alpine Linux uses `musl libc`, which occasionally causes compatibility problems with Python packages that include C extensions. The `slim` variant of the official Python image is based on Debian, which is fully `glibc`-compatible and avoids these issues while still providing a significantly reduced image size compared to the full Debian-based Python image.

---

## Demo & Testing

### Testing the Backend API with curl

After deployment, verify the backend is working correctly using `curl` from the CloudLab node or your local machine:

```bash
# Health check
curl http://<node-ip>:5000/health

# Get all tasks (initially empty)
curl http://<node-ip>:5000/tasks

# Create a task
curl -X POST http://<node-ip>:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to CloudLab", "description": "CSC 468 project"}'

# Mark task 1 as complete
curl -X PUT http://<node-ip>:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'

# Delete task 1
curl -X DELETE http://<node-ip>:5000/tasks/1
```

### Testing the Frontend

Navigate to `http://<node-ip>:5001` in a browser. You should see the task dashboard. Add a task using the form, mark it as complete, and delete it to verify full end-to-end functionality.

### Verifying Container Status

```bash
# Should show both containers as "healthy" or "Up"
docker compose ps

# Expected output:
# NAME       IMAGE                    STATUS
# backend    cloud-task-manager-backend   Up (healthy)
# frontend   cloud-task-manager-frontend  Up
```

---

*Cloud Task Manager — CSC 468 Final Project | Joseph Nweke*
