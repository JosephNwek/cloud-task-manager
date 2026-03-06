# Cloud Task Manager

## Overview

This project is a cloud-based task manager application built using containerized microservices.

The system consists of two services:

1. Frontend Web Service
2. Backend Task API Service

Both services will run in Docker containers and communicate with each other through a REST API.

---

## Vision

The goal of this project is to demonstrate a simple microservices-based cloud application.

Architecture Diagram:

User
 |
 v
Frontend Web Service
 |
REST API
 |
 v
Backend Task API Service

The frontend service will allow users to add and view tasks through a simple web interface.

The backend service will handle task management through REST API endpoints.

Both services will run inside Docker containers and communicate through a Docker network managed by Docker Compose.

---

## Proposal

The system will use the following base images:

Frontend Service
Base Image: python:3.11  
Framework: Flask  
Purpose: Provide a web interface for users to submit and view tasks.

Backend Service
Base Image: python:3.11  
Framework: Flask  
Purpose: Provide a REST API to store and retrieve tasks.

Each service will run in its own container and will communicate over HTTP using REST API requests.

Future deliverables will include implementing the application logic, connecting the services, and deploying the system in a cloud environment.
