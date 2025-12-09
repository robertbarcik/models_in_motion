# Docker - Hands-On Tutorial

This guide walks you through Docker basics: from running your first container to building custom images with Dockerfiles.

**Prerequisites:**
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Create a free account on [Docker Hub](https://hub.docker.com/)

---

## 1. Getting Started

Verify Docker is installed and running:

```bash
docker --version
docker info
```

If you see "Cannot connect to the Docker daemon", make sure Docker Desktop is started.

---

## 2. Demo A: Hello World

Run your first container:

```bash
docker run hello-world
```

This downloads the `hello-world` image from Docker Hub and runs it. You should see a confirmation message.

---

## 3. Images and Containers

**Docker images** are read-only templates containing everything needed to run an application.

**Docker containers** are running instances of images where you can interact with the application.

### View Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a
```

Output columns: `CONTAINER ID`, `IMAGE`, `COMMAND`, `CREATED`, `STATUS`, `PORTS`, `NAMES`

### View Images

```bash
docker images
```

### Download an Image

```bash
# Pull latest version
docker pull mysql

# Pull specific version
docker pull mysql:8.0
```

---

## 4. Demo B: Interactive Containers

Run a simple command in a container:

```bash
docker run busybox echo Hi friend
```

The container runs the command and exits immediately.

### Interactive Mode

To interact with a container, use `-i` (interactive) and `-t` (terminal) flags:

```bash
docker run -it busybox
```

Inside the container, try some commands:

```bash
ls
touch EmptyFile.txt
ls
exit
```

### Container Ephemerality

Start a new container and check for the file:

```bash
docker run -it busybox
ls
```

The file is gone! Each `docker run` creates a fresh container. Changes don't persist unless you commit them.

---

## 5. Demo C: Detached Mode

Run containers in the background with the `-d` flag.

### Run nginx Web Server

```bash
docker run -d -p 80:80 --name=nginx nginx
```

- `-d` — run in background (detached)
- `-p 80:80` — map host port 80 to container port 80
- `--name=nginx` — assign a name to the container

Visit http://localhost:80 in your browser to see nginx running.

### Port Mapping

The `-p` flag syntax is `-p [host_port]:[container_port]`.

To use a different port:

```bash
docker run -d -p 8080:80 --name=nginx2 nginx
```

Now accessible at http://localhost:8080

### View Container Details

```bash
docker inspect nginx
```

### View Logs

```bash
# View logs
docker logs nginx

# Follow logs in real-time (Ctrl+C to exit)
docker logs -f nginx

# Show last 50 lines, then follow
docker logs -f --tail 50 nginx
```

### Execute Commands in Running Container

```bash
# Open interactive shell
docker exec -it nginx bash

# Run single command
docker exec nginx cat /etc/nginx/nginx.conf
```

### Monitor Resource Usage

```bash
docker stats
```

Press `Ctrl+C` to exit.

### Container Lifecycle

```bash
# Stop container (graceful)
docker stop nginx

# Stop container (force)
docker kill nginx

# Start stopped container
docker start nginx

# Restart container
docker restart nginx
```

### Remove Containers and Images

```bash
# Remove stopped container
docker rm nginx

# Force remove running container
docker rm -f nginx

# Remove image
docker rmi nginx
```

Note: Remove containers before removing their images.

### Cleanup Commands

```bash
# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove all unused data (containers, networks, images, cache)
docker system prune
```

### Search Docker Hub

```bash
docker search python
```

### Important: `docker run` vs `docker start`

- `docker run` — creates a **new** container from an image
- `docker start` — starts an **existing** stopped container

---

## 6. Demo D: Building Images Manually

Create a custom image by modifying a container and committing it.

### Install Software in Container

```bash
docker run -it ubuntu bash
```

Inside the container:

```bash
apt-get update
apt-get install -y wget
wget --version
exit
```

### Commit the Container

Find your container ID:

```bash
docker ps -a
```

Create an image from it:

```bash
docker commit -m "Added wget utility" <container_id> ubuntu-with-wget:v1
```

### Verify the Image

```bash
docker images
docker run -it ubuntu-with-wget:v1 bash
wget --version
exit
```

### View Changes

```bash
docker diff <container_id>
```

- `A` = Added
- `C` = Changed
- `D` = Deleted

### Limitations of Manual Commits

- Not reproducible
- No documentation
- Error-prone
- Not version-controlled

For production, use Dockerfiles instead.

---

## 7. Demo E: Dockerfile

Dockerfiles automate image building: **Dockerfile → Image → Container**

### Create Dockerfile

```bash
mkdir MyFirstDockerfile && cd MyFirstDockerfile
nano Dockerfile
```

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*
```

- `FROM` — base image (always pin version for reproducibility)
- `RUN` — execute commands during build

### Build the Image

```bash
docker build -t ubuntudemo .
```

- `-t ubuntudemo` — name/tag the image
- `.` — build context (current directory)

Since we didn't specify a version tag (like `ubuntudemo:1.0`), Docker assigns `latest`.

### View Image History

```bash
docker history ubuntudemo
```

### The .dockerignore File

Exclude files from the build context:

```
.git
__pycache__
*.pyc
.env
*.log
node_modules
.DS_Store
```

### Layer Caching

Docker caches layers. Rebuild and notice `CACHED` steps:

```bash
docker build -t ubuntudemo .
```

If you change an early layer, all subsequent layers rebuild. Order instructions from least to most frequently changed.

### Optimizing Layers

Combine related commands to reduce layers:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

Important: Cleanup must be in the same `RUN` command, otherwise deleted files still exist in previous layers.

### Push to Docker Hub

```bash
# Login
docker login -u <username>

# Build with Docker Hub naming
docker build -t username/ubuntudemo:1.0 .

# Push
docker push username/ubuntudemo:1.0
```

### Cleanup Tip

```bash
# Remove all stopped containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)
```

---

## 8. CMD and ENTRYPOINT

Both specify what runs when a container starts, but behave differently.

| Instruction | When | Purpose |
|-------------|------|---------|
| `RUN` | Build time | Install software, setup |
| `CMD` | Runtime | Default command (easily overridden) |
| `ENTRYPOINT` | Runtime | Main executable (hard to override) |

### Shell Form vs Exec Form

```dockerfile
# Shell form
CMD wget -O- -q http://ifconfig.me/ip

# Exec form (recommended)
CMD ["wget", "-O-", "-q", "http://ifconfig.me/ip"]
```

Exec form is preferred: predictable behavior, proper signal handling, required for CMD+ENTRYPOINT combination.

### 8.1 CMD: Default Command

```bash
mkdir cmd-demo && cd cmd-demo
nano Dockerfile
```

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

CMD ["wget", "-O-", "-q", "http://ifconfig.me/ip"]
```

```bash
docker build -t cmd-demo .

# Run with default CMD
docker run cmd-demo

# Override CMD
docker run cmd-demo echo 'Hello, I replaced the default command!'
```

Note: If you see `dquote>` after pasting, the quotes may be "smart quotes". Type manually or use single quotes.

### 8.2 ENTRYPOINT: Main Executable

```bash
mkdir entrypoint-demo && cd entrypoint-demo
nano Dockerfile
```

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["wget", "-O-", "-q"]
```

```bash
docker build -t entrypoint-demo .

# Arguments are APPENDED to ENTRYPOINT
docker run entrypoint-demo http://ifconfig.me/ip

# Without arguments - fails (wget needs URL)
docker run entrypoint-demo

# Override ENTRYPOINT (requires flag)
docker run --entrypoint echo entrypoint-demo 'Hello'
```

### CMD vs ENTRYPOINT Comparison

| Aspect | CMD | ENTRYPOINT |
|--------|-----|------------|
| Purpose | Default command/arguments | Main executable |
| Override | Easy (just add command) | Hard (needs `--entrypoint`) |
| `docker run` arguments | Replace CMD | Append to ENTRYPOINT |

### 8.3 Combining ENTRYPOINT and CMD

```bash
mkdir combined-demo && cd combined-demo
nano Dockerfile
```

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["wget", "-O-", "-q"]
CMD ["http://ifconfig.me/ip"]
```

```bash
docker build -t combined-demo .

# Uses default CMD
docker run combined-demo

# Override only CMD (ENTRYPOINT stays)
docker run combined-demo http://httpbin.org/get
```

ENTRYPOINT is the fixed executable; CMD provides default arguments that can be overridden.

### When to Use What

For most ML deployments, using only ENTRYPOINT is sufficient:

```dockerfile
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:9696", "predict:app"]
```

The ENTRYPOINT+CMD combination is useful when you want a fixed executable with flexible default arguments.

---

## Quick Reference

### Container Commands

| Command | Purpose |
|---------|---------|
| `docker run <image>` | Create and start new container |
| `docker run -d` | Run in background |
| `docker run -it` | Run interactively |
| `docker run -p 8080:80` | Map ports |
| `docker run --name=myapp` | Name the container |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker stop <container>` | Stop gracefully |
| `docker start <container>` | Start stopped container |
| `docker restart <container>` | Restart container |
| `docker rm <container>` | Remove container |
| `docker logs <container>` | View logs |
| `docker logs -f <container>` | Follow logs |
| `docker exec -it <container> bash` | Shell into container |
| `docker stats` | Monitor resources |

### Image Commands

| Command | Purpose |
|---------|---------|
| `docker images` | List images |
| `docker pull <image>` | Download image |
| `docker build -t <name> .` | Build from Dockerfile |
| `docker rmi <image>` | Remove image |
| `docker push <image>` | Push to registry |
| `docker history <image>` | View layers |

### Cleanup Commands

| Command | Purpose |
|---------|---------|
| `docker rm $(docker ps -aq)` | Remove all containers |
| `docker rmi $(docker images -q)` | Remove all images |
| `docker system prune` | Remove unused data |

### Dockerfile Instructions

| Instruction | Purpose |
|-------------|---------|
| `FROM` | Base image |
| `RUN` | Execute during build |
| `CMD` | Default command (overridable) |
| `ENTRYPOINT` | Main executable |
| `COPY` | Copy files into image |
| `WORKDIR` | Set working directory |
| `EXPOSE` | Document port |

---

**Bonus:** For persistent storage, use [Docker Volumes](https://docs.docker.com/storage/volumes/).
