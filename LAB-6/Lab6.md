# Experiment 6: Docker Run vs Docker Compose

---

## Part A: Single Container (Docker Run vs Docker Compose)

### Lab 1: Running Nginx using Docker Run

```bash
mkdir html
echo "<h1>Hello from Docker Run</h1>" > html/index.html

docker run -d \
  --name lab-nginx \
  -p 8081:80 \
  -v $(pwd)/html:/usr/share/nginx/html \
  nginx:alpine
```

```bash
docker ps
```

📸 **Screenshot – nginx container running using docker run:**

![docker run nginx](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230232.png)

📸 **Screenshot – browser output:**

![browser nginx](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230243.png)

---

### Lab 2: Running Nginx using Docker Compose

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: lab-nginx
    ports:
      - "8081:80"
    volumes:
      - ./html:/usr/share/nginx/html
```

```bash
docker compose up -d
docker compose ps
```

📸 **Screenshot – docker compose up output:**

![compose up](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230355.png)

📸 **Screenshot – nginx running via compose:**

![compose nginx](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230406.png)

---

## Part B: Multi-Container Application (WordPress + MySQL)

### Lab 1: Using Docker Run

```bash
docker network create wp-net
```

📸 **Screenshot – network created:**

![network](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230415.png)

```bash
docker run -d \
  --name mysql \
  --network wp-net \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=wordpress \
  mysql:5.7
```

📸 **Screenshot – MySQL container running:**

![mysql](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230431.png)

```bash
docker run -d \
  --name wordpress \
  --network wp-net \
  -p 8082:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_PASSWORD=secret \
  wordpress:latest
```

📸 **Screenshot – WordPress container running:**

![wordpress](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230443.png)

📸 **Screenshot – WordPress browser setup:**

![wp browser](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230521.png)

---

### Lab 2: Using Docker Compose

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: wordpress
    volumes:
      - mysql_data:/var/lib/mysql

  wordpress:
    image: wordpress:latest
    ports:
      - "8082:80"
    environment:
      WORDPRESS_DB_HOST: mysql
      WORDPRESS_DB_PASSWORD: secret
    depends_on:
      - mysql

volumes:
  mysql_data:
```

```bash
docker compose up -d
```

📸 **Screenshot – compose multi-container running:**

![compose wp](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230555.png)

📸 **Screenshot – WordPress via compose browser:**

![compose wp browser](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230728.png)

---

## Part C: Conversion & Configuration Tasks

### Lab 1: Convert Docker Run to Docker Compose

```yaml
version: '3.8'

services:
  webapp:
    image: node:18-alpine
    container_name: webapp
    ports:
      - "5000:5000"
    environment:
      APP_ENV: production
      DEBUG: "false"
    restart: unless-stopped
```

```bash
docker compose up -d
docker compose ps
```

📸 **Screenshot – conversion result:**

![conversion](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230745.png)

---

### Lab 2: Volume + Network Configuration

```yaml
version: '3.8'

services:
  postgres-db:
    image: postgres:15
    container_name: postgres-db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-net

  backend:
    image: python:3.11-slim
    container_name: backend
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres-db
      DB_USER: admin
      DB_PASS: secret
    depends_on:
      - postgres-db
    networks:
      - app-net

volumes:
  pgdata:

networks:
  app-net:
```

```bash
docker compose up -d
```

📸 **Screenshot – services running with network:**

![network services](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230800.png)

📸 **Screenshot – volume created:**

![volume](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230841.png)

---

### Lab 3: Resource Limits

```yaml
version: '3.8'

services:
  limited-app:
    image: nginx:alpine
    container_name: limited-app
    ports:
      - "9000:9000"
    restart: always
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: "0.5"
```

```bash
docker compose up -d
```

📸 **Screenshot – resource limits applied:**

![limits](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230945.png)

---

## Part D: Dockerfile + Compose (Build-Based)

📸 **Screenshot – app.js created:**

![app js](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231407.png)

📸 **Screenshot – Dockerfile:**

![dockerfile](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231541.png)

```bash
docker compose up --build -d
```

📸 **Screenshot – build process:**

![build](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231557.png)

📸 **Screenshot – node app running:**

![node run](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231657.png)

---

## Part E: WordPress Compose Lab

```bash
mkdir wp-compose-lab
cd wp-compose-lab
```

📸 **Screenshot – directory setup:**

![dir](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231704.png)

```bash
docker compose up -d
```

📸 **Screenshot – final containers running:**

![final containers](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231728.png)

📸 **Screenshot – WordPress final UI:**

![final wp](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231746.png)

📸 **Screenshot – volumes list:**

![volumes](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231834.png)

---

## Key Takeaways

- **Docker Run** is imperative — commands are written one by one
- **Docker Compose** is declarative — entire stack defined in a single YAML file
- Compose simplifies multi-container application management
- **Volumes** ensure data persistence across container restarts
- **Networks** enable seamless communication between containers
- `deploy` resource limits work only in Swarm mode
- **Build** directive in Compose enables custom image creation

---
