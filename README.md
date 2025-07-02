# 🎬 Movie Management System

A full-stack movie management web application built using **Flask**, **Streamlit**, and **MongoDB**. The system allows users to explore, search, and manage movies with an interactive user interface powered by Streamlit. Data is stored and retrieved from MongoDB, and Flask serves as the backend API layer.

---

## 📌 Features

- 🎥 Browse and search for movies
- 🔎 Filter by genre, rating, or title
- 📊 Interactive Streamlit frontend
- 🧠 Backend API powered by Flask
- 🗄️ MongoDB for persistent data storage
- 🐳 Docker support for local development
- ☸️ Kubernetes manifests for production deployment

---

## ⚙️ Tech Stack

| Layer       | Technology         |
|------------|--------------------|
| Frontend    | Streamlit         |
| Backend     | Flask (Python)    |
| Database    | MongoDB           |
| Cloud       | AWS ec2           |
| CI/CD       | GitHub Actions    |
| Orchestration |  Kubernetes      |
| Deployment      | Docker, Docker Compose|

---

## 🚀 Setup & Installation

### 🐳 Option 1: Local Development with Docker 

1. Ensure [Docker](https://www.docker.com/products/docker-desktop/) is installed and running.
2. Create a .env file in the project root with the following content:
   - MONGO_DATABASE,DATABASE_NAME, MONGO_ROOT_USERNAME, MONGO_ROOT_PASSWORD
   - SECRET_KEY,FLASK_ENV
3. Pull and start the containers using Docker Compose:
   ```bash
   docker-compose up --build -d


### ☸️ Option 2: Kubernetes

1. Ensure [k3d](https://k3d.io/stable/) and [kubectl](https://kubernetes.io/docs/tasks/tools/) are installed.
2. Create a Kubernetes cluster using k3d with a load balancer \
k3d cluster create movie              
  --api-port 6550 \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer" \
  --port "443:443@loadbalancer"
3. cd kubernetes
4. ⚠️ The order is important due to resource dependencies.  \
   Apply the Kubernetes manifests in the correct order.
  ```bash
  kubectl apply -f namespace.yaml /
  kubectl apply -f configmaps.yaml /
  kubectl apply -f secrets.yaml /
  kubectl apply -f statefulsets.yaml /
  kubectl apply -f services.yaml  /
  kubectl apply -f backend-deployment.yaml /
  kubectl apply -f frontend-deployment.yaml /
  kubectl apply -f ingress.yaml
