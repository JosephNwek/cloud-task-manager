# Cloud Task Manager

**Author:** Joseph Nweke  
**Course:** CSC 468 - Introduction to Cloud Computing

## Vision

The goal of this project is to build a simple cloud-based task management system using containerized services.

### Tasks Managed

The Cloud Task Manager infrastructure will manage the following tasks:

- Create new tasks (title, description, due date)
- List all tasks
- Mark tasks as completed
- Delete tasks
- Optionally, filter tasks by status (pending/completed)

### System Components

- Frontend Web Application
- Backend Task API

The frontend communicates with the backend through a REST API.

### Architecture Diagram

```
+------------------+
|       User       |
+------------------+
        |
        v
+------------------+
|  Frontend App    |
|  (Flask Service) |
+------------------+
        |
     REST API
        |
        v
+------------------+
|  Backend API     |
|  (Flask Service) |
+------------------+
```
---

## Proposal

This project will use **Docker containers** to run two services: frontend and backend.

### Frontend Service

- **Base Image:** Python  
- **Framework:** Flask  
- **Purpose:** Provide the web interface where users can create and view tasks.

### Backend Service

- **Base Image:** Python  
- **Framework:** Flask  
- **Purpose:** Provide REST API endpoints that store and manage task data.

The frontend and backend services will communicate through **HTTP requests using a REST API**.
