# Experiment 11: Orchestration using Docker Compose & Docker Swarm

---

## Part A: Concept Continuation

### From Experiment 6 to Orchestration

| Tool | What it does | Limitation |
|---|---|---|
| `docker run` | Runs a single container | Manual, no coordination |
| Docker Compose | Runs multiple containers together | Single machine, no auto-healing |
| Docker Swarm | Orchestrates containers across nodes | Basic compared to Kubernetes |

**Orchestration** = Automatic management of containers. Think of it like a restaurant manager:
- Decides how many waiters are needed **(scaling)**
- Replaces a sick waiter immediately **(self-healing)**
- Distributes customers evenly **(load balancing)**

### The Progression Path

```
docker run  →  Docker Compose  →  Docker Swarm  →  Kubernetes
    │               │                  │                │
Single         Multi-container     Orchestration     Advanced
container      (single host)         (basic)       orchestration
```

---

## Part B: Practical (Extension of Experiment 6)

### Prerequisites

The `docker-compose.yml` from Experiment 6 (WordPress + MySQL):

```yaml
version: '3.9'

services:
  db:
    image: mysql:5.7
    container_name: wordpress_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass
    volumes:
      - db_data:/var/lib/mysql

  wordpress:
    image: wordpress:latest
    container_name: wordpress_app
    depends_on:
      - db
    ports:
      - "8080:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html

volumes:
  db_data:
  wp_data:
```

---

### Task 1: Check Current State (No Swarm)

```bash
# Stop any existing compose setup
docker compose down -v

# Verify no containers are running
docker ps
```

📸 **Screenshot – docker compose down -v and docker ps showing empty container list:**

![task1 clean state](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20085921.png)

---

### Task 2: Initialize Docker Swarm

```bash
docker swarm init
```

This enables Swarm mode and makes the current node a **manager** (Leader).

```bash
docker node ls
```

📸 **Screenshot – docker swarm init output and docker node ls showing node as Leader:**

![swarm init](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090001.png)

---

### Task 3: Deploy as a Stack

```bash
docker stack deploy -c docker-compose.yml wpstack
```

📸 **Screenshot – docker stack deploy creating network wpstack_default and services wpstack_wordpress, wpstack_db:**

![stack deploy](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090438.png)

---

### Task 4: Verify the Deployment

```bash
docker service ls
```

📸 **Screenshot – docker service ls showing wpstack_db (1/1) and wpstack_wordpress (0/1 starting):**

![service ls](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090448.png)

```bash
docker service ps wpstack_wordpress
```

📸 **Screenshot – docker service ps showing wpstack_wordpress.1 Preparing on docker-desktop:**

![service ps](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090457.png)

```bash
docker ps
```

📸 **Screenshot – docker service ps and docker ps showing mysql container running (Swarm-managed):**

![docker ps swarm](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090504.png)

---

### Task 5: Access WordPress

Open your browser at `http://localhost:8080`

📸 **Screenshot – WordPress installation page at localhost:8080:**

![wordpress browser](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090705.png)

---

### Task 6: Scale the Application (Swarm's Superpower)

```bash
docker service scale wpstack_wordpress=3
```

📸 **Screenshot – docker service scale output: 3/3 tasks running, service converged:**

![scale output](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090723.png)

```bash
docker service ls
docker ps | grep wordpress
```

📸 **Screenshot – docker service ls showing REPLICAS 3/3, docker ps showing 3 WordPress containers:**

![scale verified](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090743.png)

**What just happened?**

| Before Scaling | After Scaling |
|---|---|
| 1 WordPress container | 3 WordPress containers |
| No load distribution | Swarm balances traffic |
| Manual scaling needed | One command scaling |

> Swarm's internal load balancer listens on port 8080 once and distributes requests across all 3 containers automatically.

---

### Task 7: Test Self-Healing (Automatic Recovery)

```bash
# Kill one container to simulate a crash
docker kill <container-id>

# Watch Swarm recreate it
docker service ps wpstack_wordpress
```

📸 **Screenshot – docker kill, then docker service ps showing killed container as Shutdown/Failed and new replacement Running:**

![self healing](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090842.png)

> **Self-healing:** The killed container shows `Shutdown / Failed` while a new one is automatically created — total replicas still = 3, no manual intervention needed.

---

### Task 8: Remove the Stack

```bash
docker stack rm wpstack
docker service ls
docker ps
```

📸 **Screenshot – docker stack rm removing all services and network, docker service ls and docker ps showing empty:**

![stack rm](../LAB-11/SCREENSHOTS/Screenshot%202026-05-01%20090905.png)

---

## Part C: Analysis (Compose vs Swarm)

| Feature | Docker Compose | Docker Swarm |
|---|---|---|
| Scope | Single host only | Multi-node cluster |
| Scaling | `--scale` (no load balancing) | `docker service scale` (built-in LB) |
| Load Balancing | No (port conflicts) | Yes (internal LB) |
| Self-Healing | No (manual restart) | Yes (automatic) |
| Rolling Updates | No | Yes (zero downtime) |
| Use Case | Development, testing | Simple production clusters |

**When to use what:**
```
Development   ──► Compose
Testing       ──► Compose
Small Prod    ──► Swarm
Large Prod    ──► Kubernetes
```

---

## Key Takeaways

- **Same YAML file** works for both `docker compose up` and `docker stack deploy` — Swarm extends Compose, not replaces it
- In Swarm you manage **services**, not individual containers
- Swarm's internal load balancer solves the port conflict problem when scaling
- **Self-healing** maintains the desired replica count without any manual intervention

---

## Quick Reference Card

```bash
docker swarm init
docker stack deploy -c docker-compose.yml <stack-name>
docker service ls
docker service scale <stack>_<service>=<replicas>
docker service ps <service-name>
docker stack rm <stack-name>
docker swarm leave --force
```

---
