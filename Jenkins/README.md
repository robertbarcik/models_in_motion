# Jenkins CI/CD - Hands-On Tutorial

This guide covers Jenkins basics: setting up with Docker, creating pipelines, and automating Python project builds.

---

## 1. Introduction

Jenkins is an open-source automation server for continuous integration and continuous delivery (CI/CD). It automates the build, test, and deployment of applications, streamlining the software development pipeline.

Jenkins helps teams:
- Catch bugs early through automated testing
- Improve code quality
- Deliver updates faster and more reliably
- Integrate changes continuously without manual intervention

---

## 2. Core Features

### Pipeline as Code

Define build/test/deploy workflows as code in a `Jenkinsfile`. This allows version control of your CI/CD process and supports complex automation with multiple stages, parallel steps, and approvals.

### Extensible Plugin Architecture

Over 1,900 plugins available for integration with virtually any tool: Git, Docker, Kubernetes, Slack, Python environments, test reporting, and more.

### Distributed Builds (Master-Agent)

Run builds across multiple machines (agents) for parallel execution and different environments. Agents can be Linux, macOS, Windows, or containers.

### Version Control Integration

Out-of-the-box support for Git, GitHub, Bitbucket, Subversion. Jenkins can poll repositories or receive webhooks to trigger builds on code commits.

### Web-Based Dashboard

Configure jobs, monitor builds, view results, and access logs through the web UI. REST APIs available for automation.

---

## 3. Architecture

### Master-Agent Architecture

**Controller (Master):**
- Schedules build jobs
- Dispatches jobs to agents
- Monitors execution
- Provides web interface
- Maintains configuration and build history

**Agents:**
- Worker nodes on other machines or containers
- Execute build tasks
- Report results back to controller
- Can be on various OS or containerized environments

### Job Execution Flow

1. Developer pushes code to Git repository
2. Webhook notifies Jenkins (or Jenkins polls)
3. Controller schedules job and assigns to agent
4. Agent checks out code and runs build stages
5. Jenkins aggregates results and notifies team

---

## 4. Installation with Docker

### Prerequisites

- Docker Desktop installed and running

### Run Jenkins Container

```bash
docker run \
  -p 8080:8080 -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  jenkins/jenkins:lts
```

- Port `8080` — Jenkins web UI
- Port `50000` — Agent connections
- Volume `~/jenkins_home` — Persists Jenkins data

### Initial Setup

1. Wait for Jenkins to start. Look for the initial admin password in the terminal output:

```
Please use the following password to proceed to installation:
abcdefghijklmn
```

2. Open http://localhost:8080 in your browser

3. Paste the initial admin password and click **Continue**

4. Choose **Install suggested plugins**

5. Create your admin user (username, password, email)

6. Accept the default Jenkins URL

7. Jenkins is ready!

### Managing the Container

```bash
# Stop Jenkins (if running in foreground)
Ctrl+C

# Start existing container
docker start <container_name>

# Stop container (detached mode)
docker stop <container_name>
```

---

## 5. Practical Example: Python CI/CD Pipeline

We'll create a complete CI/CD pipeline for a Python string cleaning utility.

### Step 1: Create Project Structure

```bash
mkdir string_cleaner
cd string_cleaner
mkdir cleaner tests
```

### Step 2: Create Python Utility

Create `cleaner/string_utils.py`:

```python
import re

def clean_string(text):
    """
    Cleans input text by removing leading/trailing spaces,
    converting to lowercase, and removing special characters.
    """
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9 ]+', '', text)
    return text.strip()
```

### Step 3: Create Tests

Create `tests/test_string_utils.py`:

```python
from cleaner import string_utils

def test_clean_string_basic():
    assert string_utils.clean_string("  Hello World!  ") == "hello world"

def test_clean_string_symbols():
    assert string_utils.clean_string("##Welcome***To@@Python!!") == "welcometopython"

def test_clean_string_numbers():
    assert string_utils.clean_string("  Data 123 ###  ") == "data 123"
```

### Step 4: Create Requirements File

Create `requirements.txt`:

```txt
pytest
pytest-cov
```

### Step 5: Test Locally (Optional)

```bash
pip install -r requirements.txt

PYTHONPATH=. pytest --cov=cleaner --cov-report=xml:coverage.xml --cov-report=html --junitxml=pytest-results.xml
```

You should see all 3 tests pass.

### Step 6: Install Docker Pipeline Plugin

1. In Jenkins, go to **Manage Jenkins** → **Plugins**
2. Go to **Available Plugins** tab
3. Search for **Docker Pipeline**
4. Check the box and install it

### Step 7: Create Jenkins Pipeline Job

1. From Jenkins dashboard, click **New Item**
2. Name: `Python_CI_string_cleaner`
3. Select **Pipeline**
4. Click **OK**

### Step 8: Configure Pipeline Script

Scroll to **Pipeline** section, set **Definition** to `Pipeline script`, and paste:

```groovy
pipeline {
    agent {
        docker { image 'python:3.10' }
    }

    stages {
        stage('Create Project') {
            steps {
                sh '''
                    mkdir -p cleaner tests

                    echo "import re\\n\\ndef clean_string(text):\\n    text = text.strip().lower()\\n    text = re.sub(r'[^a-z0-9 ]+', '', text)\\n    return text.strip()" > cleaner/string_utils.py

                    echo "from cleaner import string_utils\\n\\ndef test_clean_string_basic():\\n    assert string_utils.clean_string(' Hello World! ') == 'hello world'\\n\\ndef test_clean_string_symbols():\\n    assert string_utils.clean_string('##Welcome***To@@Python!!') == 'welcometopython'\\n\\ndef test_clean_string_numbers():\\n    assert string_utils.clean_string(' Data 123 ### ') == 'data 123'" > tests/test_string_utils.py

                    echo "pytest\\npytest-cov" > requirements.txt
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest --junitxml=pytest-results.xml --cov=cleaner --cov-report=xml:coverage.xml --cov-report=html'
            }
        }

        stage('Publish Results') {
            steps {
                junit 'pytest-results.xml'
                archiveArtifacts artifacts: 'coverage.xml'
                archiveArtifacts artifacts: 'htmlcov/**'
            }
        }
    }
}
```

Click **Save**.

### Step 9: Run the Pipeline

1. Click **Build Now**
2. Watch the build in **Stage View**
3. Click into the build to see:
   - Console output
   - Test results
   - Coverage artifacts

---

## 6. Understanding the Pipeline

### Pipeline Structure

```groovy
pipeline {
    agent { ... }      // Where to run
    stages {
        stage('Name') {
            steps { ... }  // What to do
        }
    }
}
```

### Agent with Docker

```groovy
agent {
    docker { image 'python:3.10' }
}
```

Runs the pipeline inside a Python 3.10 Docker container, ensuring a clean, consistent environment.

### Stages

| Stage | Purpose |
|-------|---------|
| Create Project | Set up project files |
| Install Dependencies | `pip install` requirements |
| Run Tests | Execute pytest with coverage |
| Publish Results | Archive reports for Jenkins UI |

### Test Reports

- `pytest-results.xml` — JUnit-style test results (displayed in Jenkins)
- `coverage.xml` — Machine-readable coverage report
- `htmlcov/` — Human-readable HTML coverage report

---

## 7. Best Practices

### Use Jenkinsfiles (Pipeline as Code)

Store pipeline configuration in a `Jenkinsfile` in your repository instead of configuring through the GUI. Benefits:
- Version controlled
- Reviewable
- Reproducible

### Secure Secrets with Credentials Store

Never hardcode passwords or API keys. Use Jenkins Credentials plugin:

```groovy
withCredentials([string(credentialsId: 'my-api-key', variable: 'API_KEY')]) {
    sh 'deploy.sh $API_KEY'
}
```

### Manage Plugins Wisely

- Install only plugins you need
- Keep plugins updated
- Remove unused plugins
- Prefer well-maintained, popular plugins

### Run Builds on Agents

- Don't run builds on the controller
- Use Docker agents for clean environments
- Scale by adding more agents

### Monitor Resources

- Watch CPU, memory, disk usage
- Set up notifications for failed builds (email, Slack)
- Add agents if builds queue up

### Backup Jenkins Data

The `JENKINS_HOME` directory contains all configuration. Back it up regularly:
- `jobs/` — Job configurations
- `config.xml` — Global configuration
- `credentials.xml` — Stored credentials

### Security

- Keep Jenkins and plugins updated
- Use role-based access control
- Secure with SSL for internet-facing instances
- Be mindful of what code your jobs execute

---

## Quick Reference

### Docker Commands

| Command | Purpose |
|---------|---------|
| `docker run -p 8080:8080 jenkins/jenkins:lts` | Start Jenkins |
| `docker start <container>` | Start existing container |
| `docker stop <container>` | Stop container |

### Jenkins URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8080` | Jenkins dashboard |
| `http://localhost:8080/job/<name>` | Job page |
| `http://localhost:8080/manage` | Manage Jenkins |

### Pipeline Syntax

```groovy
pipeline {
    agent { docker { image 'python:3.10' } }

    environment {
        MY_VAR = 'value'
    }

    stages {
        stage('Build') {
            steps {
                sh 'echo "Building..."'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'deploy.sh'
            }
        }
    }

    post {
        always {
            junit 'results.xml'
        }
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
```

### Common Pipeline Steps

| Step | Purpose |
|------|---------|
| `sh 'command'` | Run shell command |
| `checkout scm` | Check out source code |
| `junit 'results.xml'` | Publish test results |
| `archiveArtifacts artifacts: 'file'` | Archive files |
| `withCredentials([...])` | Use credentials |
| `echo 'message'` | Print message |

### Useful Plugins

| Plugin | Purpose |
|--------|---------|
| Docker Pipeline | Run builds in Docker containers |
| Git | Git integration |
| GitHub | GitHub webhooks and status |
| JUnit | Test result reporting |
| Cobertura | Coverage reporting |
| Slack Notification | Slack integration |
| Blue Ocean | Modern UI |
