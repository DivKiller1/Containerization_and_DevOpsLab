# Lab 6: Docker Run vs Docker Compose

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

📸 **Screenshot – docker run command executing, container ID returned:**

![docker run nginx](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230232.png)

```bash
docker ps
```

📸 **Screenshot – docker ps showing lab-nginx running on port 8081:**

![docker ps nginx](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230243.png)

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
```

📸 **Screenshot – docker compose up creating network and starting container:**

![compose up](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230355.png)

```bash
docker compose ps
```

📸 **Screenshot – docker compose ps showing lab-nginx running:**

![compose ps](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230406.png)

```bash
docker compose down
```

📸 **Screenshot – docker compose down removing container and network:**

![compose down](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230415.png)

---

## Part B: Multi-Container Application (WordPress + MySQL)

### Lab 1: Using Docker Run

```bash
docker network create wp-net
```

```bash
docker run -d \
  --name mysql \
  --network wp-net \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=wordpress \
  mysql:5.7
```

📸 **Screenshot – network created and MySQL container started:**

![network and mysql](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230431.png)

```bash
docker run -d \
  --name wordpress \
  --network wp-net \
  -p 8082:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_PASSWORD=secret \
  wordpress:latest
```

📸 **Screenshot – WordPress container started:**

![wordpress run](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230443.png)

📸 **Screenshot – Browser at localhost:8082 (DB connection error while containers initialize):**

![wp browser error](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230521.png)

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

📸 **Screenshot – docker-compose.yml file in nano editor:**

![compose yml](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230555.png)

```bash
docker compose up -d
```

📸 **Screenshot – docker compose up starting MySQL and WordPress containers:**

![compose wp up](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230728.png)

```bash
docker compose down -v
```

📸 **Screenshot – docker compose down -v removing containers, volumes and network:**

![compose wp down](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230745.png)

---

## Part C: Conversion & Configuration Tasks

### Lab 1: Convert Docker Run to Docker Compose

**Given Docker Run command:**

```bash
docker run -d \
  --name webapp \
  -p 5000:5000 \
  -e APP_ENV=production \
  -e DEBUG=false \
  --restart unless-stopped \
  node:18-alpine
```

📸 **Screenshot – docker run webapp command executing:**

![docker run webapp](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230800.png)

**Equivalent docker-compose.yml:**

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

📸 **Screenshot – docker-compose.yml equivalent in nano editor:**

![webapp compose yml](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230841.png)

```bash
docker compose up -d
docker compose ps
```

📸 **Screenshot – webapp compose up and ps output:**

![webapp compose up](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20230945.png)

---

### Lab 2: Volume + Network Configuration

**Given Docker Run commands:**

```bash
docker network create app-net

docker run -d \
  --name postgres-db \
  --network app-net \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15

docker run -d \
  --name backend \
  --network app-net \
  -p 8000:8000 \
  -e DB_HOST=postgres-db \
  -e DB_USER=admin \
  -e DB_PASS=secret \
  python:3.11-slim
```

**Equivalent docker-compose.yml:**

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
docker compose down -v
```

📸 **Screenshot – postgres-db and backend compose up, then down -v with volumes and network removed:**

![volume network compose](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231407.png)

---

### Lab 3: Resource Limits Conversion

**Given Docker Run command:**

```bash
docker run -d \
  --name limited-app \
  -p 9000:9000 \
  --memory="256m" \
  --cpus="0.5" \
  --restart always \
  nginx:alpine
```

**Equivalent docker-compose.yml:**

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

📸 **Screenshot – resource limits docker-compose.yml in nano editor:**

![resource limits yml](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231541.png)

```bash
docker compose up -d
docker compose down
```

📸 **Screenshot – limited-app compose up and down:**

![resource limits run](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231557.png)

---

## Part D: Dockerfile + Compose (Build-Based)

### Lab 1: Create the Node.js Application

**Step 1: Create app.js**

```javascript
const http = require('http');

http.createServer((req, res) => {
  res.end("Docker Compose Build Lab");
}).listen(3000);
```

📸 **Screenshot – app.js in nano editor:**

![app js](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231704.png)

**Step 2: Create Dockerfile**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY app.js .

EXPOSE 3000

CMD ["node", "app.js"]
```

📸 **Screenshot – Dockerfile in nano editor:**

![dockerfile](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231657.png)

**Step 3: Create docker-compose.yml with build:**

```yaml
version: '3.8'

services:
  nodeapp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: custom-node-app
    ports:
      - "3000:3000"
```

📸 **Screenshot – build-based docker-compose.yml in nano editor:**

![build compose yml](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231728.png)

---

### Lab 2: Build and Run

```bash
docker compose up --build -d
```

📸 **Screenshot – docker compose up --build, image built and container started:**

![compose build](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231746.png)

📸 **Screenshot – browser at localhost:3000 showing "Docker Compose Build Lab":**

![node app browser](../LAB-6/SCREENSHOTS/Screenshot%202026-03-21%20231834.png)

---

## Key Takeaways

- **Docker Run** is imperative — flags are written explicitly per command
- **Docker Compose** is declarative — entire stack defined in a single YAML file
- Compose simplifies multi-container application management
- **Volumes** ensure data persistence across container restarts
- **Networks** enable seamless communication between containers
- `deploy.resources` limits work only in Swarm mode; in standalone Compose they are accepted but not enforced
- **`build:`** directive in Compose replaces `image:` to build from a local Dockerfile

---
