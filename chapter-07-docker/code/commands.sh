#!/bin/bash
# ============================================================
# Chapter 7: Docker
# Commands from demos A-D and other sections.
# Demos E-G have their own folders with Dockerfiles and code.
# ============================================================


# ============================================================
# Demo A: Hello World
# ============================================================

docker --version
docker info
docker run hello-world

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List all images
docker images

# Pull an image from Docker Hub
docker pull mysql


# ============================================================
# Demo B: Interaction
# ============================================================

# Run a command in a container
docker run busybox echo Hi friend

# Run interactive container with terminal
docker run -it busybox
# Inside: touch EmptyFile.txt, ls, exit


# ============================================================
# Demo C: Detached mode
# ============================================================

# Run nginx in detached mode with port mapping
docker run -d -p 80:80 --name=nginx nginx
docker run -d -p 8080:80 --name=nginx2 nginx

# Inspect container details
docker inspect nginx

# View and follow logs
docker logs nginx
docker logs -f nginx
docker logs -f --tail 50 nginx

# Execute command inside running container
docker exec -it nginx bash

# Resource usage statistics
docker stats

# Stop, start, restart containers
docker stop nginx
docker kill nginx2
docker start nginx
docker restart nginx

# Remove containers and images
docker rm <container_id>
docker rmi <image_name>

# Cleanup commands
docker image prune
docker image prune -a
docker container prune
docker system prune

# Search Docker Hub
docker search python

# Bulk cleanup
docker rm $(docker ps -aq)
docker rmi $(docker images -q)


# ============================================================
# Demo D: Our own Docker image (manual approach)
# ============================================================

docker run -it ubuntu bash
# Inside: apt-get update && apt-get install -y wget

# Commit container as new image
docker commit -m "Added wget utility" <container_id> ubuntu-with-wget:v2

# Inspect changes
docker diff <container_id>


# ============================================================
# Demo E: Dockerfile - see demo_e_dockerfile/ folder
# ============================================================

cd demo_e_dockerfile
docker build -t ubuntudemo .
docker history <image_id>

# Push to Docker Hub
docker build -t username/ubuntudemo:2.0 .
docker login -u <username>
docker push username/ubuntudemo:2.0


# ============================================================
# Demo F: Dockerizing a Python script - see demo_f_python/ folder
# ============================================================

cd demo_f_python
docker build -t python-docker-demo .
docker run python-docker-demo


# ============================================================
# Demo G: Docker Compose - see demo_g_compose/ folder
# ============================================================

cd demo_g_compose
docker-compose up
docker-compose down
docker-compose up -d
docker-compose logs
