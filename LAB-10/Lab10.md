# Experiment 10: SonarQube — Static Code Analysis

---

## Theory

**Problem Statement:** Code bugs and security issues are often found too late — during testing or even after deployment. Manual code reviews are slow, inconsistent, and don't scale as teams grow.

**What is SonarQube?** SonarQube is an open-source platform that automatically scans your source code for bugs, security vulnerabilities, and maintainability issues — without running the code. This is called **static analysis**.

**How SonarQube Solves the Problem:**
- Scans code on every commit, giving immediate feedback
- Enforces **Quality Gates** — pass/fail checks before code is deployed
- Tracks **Technical Debt** — estimated time to fix all issues
- Supports 20+ programming languages
- Provides a visual dashboard for trends over time

**Key Terms:**

| Term | What it means |
|---|---|
| Quality Gate | A set of rules; code must pass before deployment |
| Bug | Code that will likely break or behave incorrectly |
| Vulnerability | A security weakness in the code |
| Code Smell | Code that works but is poorly written or hard to maintain |
| Technical Debt | Estimated time to fix all issues |
| Coverage | Percentage of code tested by unit tests |
| Duplication | Repeated code blocks (copy-paste) |

---

## Lab Architecture

SonarQube has two separate components — a **Server** (the brain) and a **Scanner** (the worker). Both are required.

```
[ Your Code ]
      │
      ▼
[ Sonar Scanner ]  ◀── reads code, detects issues
      │
      │  sends analysis report (HTTP + Token)
      ▼
[ SonarQube Server ]  ◀── validates, stores, displays results
      │
      ▼
[ PostgreSQL Database ]  ◀── persists everything
```

| Feature | SonarQube Server | Sonar Scanner |
|---|---|---|
| Type | Server application | CLI / plugin |
| Role | Store & display results | Analyze code |
| Web UI | Yes (port 9000) | No |
| Runs on | Server / Docker container | Dev machine / CI |
| Required | Yes | Yes |

---

## Step 1: Start the SonarQube Server

We use Docker to start both the SonarQube server and its PostgreSQL database.

### 1a. Create the network and start the database

```bash
docker network create sonarqube-lab

docker run -d \
  --name sonar-db \
  --network sonarqube-lab \
  -e POSTGRES_USER=sonar \
  -e POSTGRES_PASSWORD=sonar \
  -e POSTGRES_DB=sonarqube \
  -v sonar-db-data:/var/lib/postgresql/data \
  postgres:13
```

📸 **Screenshot – sonarqube-lab network created and postgres:13 container pulled and started:**

![sonar-db started](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143059.png)

---

### 1b. Start the SonarQube Server container

```bash
docker run -d \
  --name sonarqube \
  --network sonarqube-lab \
  -p 9000:9000 \
  -e SONAR_JDBC_URL=jdbc:postgresql://sonar-db:5432/sonarqube \
  -e SONAR_JDBC_USERNAME=sonar \
  -e SONAR_JDBC_PASSWORD=sonar \
  -v sonar-data:/opt/sonarqube/data \
  -v sonar-extensions:/opt/sonarqube/extensions \
  sonarqube:lts-community
```

📸 **Screenshot – sonarqube:lts-community image pulled and container started:**

![sonarqube started](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143218.png)

---

### 1c. Watch logs until server is ready

```bash
docker logs -f sonarqube
```

📸 **Screenshot – SonarQube logs showing "SonarQube is operational":**

![sonarqube logs](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143344.png)

---

### 1d. Verify both containers are running

```bash
docker ps
```

📸 **Screenshot – docker ps showing sonarqube (port 9000) and sonar-db running:**

![docker ps](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143422.png)

---

### 1e. Access the Web UI

Open `http://localhost:9000` in your browser. Default login: `admin` / `admin`.

📸 **Screenshot – SonarQube login page at localhost:9000:**

![sonarqube login](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143513.png)

---

### 1f. Verify server is responding (CLI)

```bash
curl localhost:9000
```

📸 **Screenshot – curl localhost:9000 returning SonarQube HTML (server UP):**

![curl sonarqube](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20145639.png)

---

## Step 2: Create a Sample Java App with Code Issues

```bash
mkdir -p sample-java-app/src/main/java/com/example
cd sample-java-app
```

**`src/main/java/com/example/Calculator.java`:**

```java
package com.example;

public class Calculator {

    // BUG: Division by zero is not handled
    public int divide(int a, int b) {
        return a / b;
    }

    // CODE SMELL: Unused variable
    public int add(int a, int b) {
        int result = a + b;
        int unused = 100;   // ← delete this
        return result;
    }

    // VULNERABILITY: SQL Injection risk
    public String getUser(String userId) {
        String query = "SELECT * FROM users WHERE id = " + userId;
        return query;
    }

    // CODE SMELL: Duplicated code
    public int multiply(int a, int b) {
        int result = 0;
        for (int i = 0; i < b; i++) { result = result + a; }
        return result;
    }

    public int multiplyAlt(int a, int b) {
        int result = 0;
        for (int i = 0; i < b; i++) { result = result + a; }  // exact duplicate
        return result;
    }

    // BUG: Null pointer risk
    public String getName(String name) {
        return name.toUpperCase();  // throws NullPointerException if null
    }

    // CODE SMELL: Empty catch block
    public void riskyOperation() {
        try {
            int x = 10 / 0;
        } catch (Exception e) {
            // never leave catch blocks empty
        }
    }
}
```

**`pom.xml`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" ...>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>sample-app</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <sonar.projectKey>sample-java-app</sonar.projectKey>
        <sonar.host.url>http://localhost:9000</sonar.host.url>
        <sonar.login>YOUR_TOKEN_HERE</sonar.login>
    </properties>

    <build>
        <plugins>
            <plugin>
                <groupId>org.sonarsource.scanner.maven</groupId>
                <artifactId>sonar-maven-plugin</artifactId>
                <version>3.9.1.2184</version>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Step 3: Create a Project and Generate a Token

### 3a. Create project manually in the UI

Navigate to `http://localhost:9000/projects/create` and select **Manually**.

📸 **Screenshot – Create project page showing DevOps platform options and "Manually":**

![create project](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20143558.png)

---

### 3b. Generate a scanner token

1. Click your user icon (top right) → **My Account**
2. Click the **Security** tab
3. Under **Generate Tokens**, enter a name: `exp10`
4. Click **Generate**
5. **Copy the token immediately** — it is shown only once!

📸 **Screenshot – Token "exp10" generated and displayed (copy immediately):**

![token generated](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20144326.png)

> Token format: `sqa_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
> Store it safely — you **cannot** retrieve it again after closing this page.

---

## Step 4: Run the Scanner

**Option A — Maven Plugin (recommended for Java):**

```bash
cd sample-java-app
mvn sonar:sonar -Dsonar.login=YOUR_TOKEN
```

**Option B — Sonar Scanner CLI via Docker:**

Create `sonar-project.properties`:

```properties
sonar.projectKey=sample-java-app
sonar.projectName=Sample Java Application
sonar.projectVersion=1.0
sonar.sources=src
sonar.java.binaries=target/classes
sonar.sourceEncoding=UTF-8
```

Then run the scanner container:

```bash
docker run --rm \
  --network sonarqube-lab \
  -e SONAR_TOKEN="YOUR_TOKEN" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.projectBaseDir=/usr/src
```

> Note: Use `http://sonarqube:9000` (container name) not `localhost` when running via Docker network.

---

## Step 5: View Results in the Dashboard

### 5a. Projects overview — Quality Gate status

📸 **Screenshot – Projects page: Sample Java App with Quality Gate "Passed", 3 Code Smells detected:**

![projects passed](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20145716.png)

---

### 5b. Issues view — Detailed findings

📸 **Screenshot – Issues page: 3 Code Smells in Calculator.java (unused variable, clumsy code):**

![issues list](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20150049.png)

---

### 5c. Project dashboard — Quality Gate details

📸 **Screenshot – sample-app dashboard: Quality Gate Failed (Security Hotspots Reviewed < 100%), 1 New Security Hotspot:**

![dashboard failed](../LAB-10/SCREENSHOTS/Screenshot%202026-04-18%20150849.png)

---

### 5d. Query results via API

```bash
# List all bugs found in the project (returns JSON)
curl -u admin:YOUR_TOKEN \
  "http://localhost:9000/api/issues/search?projectKeys=sample-java-app&types=BUG"
```

---

## Step 6: Integrate with Jenkins (CI/CD)

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn clean verify sonar:sonar'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build') {
            steps { sh 'mvn package' }
        }

        stage('Deploy') {
            steps {
                sh 'docker build -t sample-app .'
                sh 'docker run -d -p 8080:8080 sample-app'
            }
        }
    }
}
```

**Pipeline flow:**
```
Checkout → SonarQube Analysis → Quality Gate → Build → Deploy
                                      │
                               FAIL? Pipeline stops.
                               Code is NOT deployed.
```

---

## Key Takeaways

- **SonarQube Server** stores and displays results; **Sonar Scanner** reads code and sends the report — both are required
- The Scanner authenticates using a **token** generated in the Server UI — never a username/password
- **Quality Gates** enforce code quality thresholds — if they fail, the pipeline stops and code is not deployed
- **Technical Debt** gives a time estimate to fix all detected issues
- SonarQube integrates with Jenkins, GitHub Actions, and other CI/CD tools for automated scanning on every commit
- Never hardcode tokens in source files — use environment variables or a secrets manager

---
