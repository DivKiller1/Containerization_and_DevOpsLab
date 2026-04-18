# Experiment 9: Ansible

---

## Theory

**Problem Statement:** Managing infrastructure manually across multiple servers leads to configuration drift, inconsistent environments, and time-consuming repetitive tasks. Scaling from one server to hundreds becomes nearly impossible with manual SSH-based administration.

**What is Ansible?**
Ansible is an open-source automation tool for configuration management, application deployment, and orchestration. It follows an agentless architecture, using SSH for Linux and WinRM for Windows, and uses YAML-based playbooks to define automation tasks.

**How Ansible Solves the Problem:**
- **Agentless Architecture:** No software installation required on managed nodes
- **Idempotency:** Running playbooks multiple times yields the same result
- **Declarative Syntax:** Describe desired state, not steps to achieve it
- **Push-based:** Initiates changes from control node immediately

**Key Concepts:**

| Component | Description |
|---|---|
| Control Node | Machine with Ansible installed |
| Managed Nodes | Target servers (no Ansible agent needed) |
| Inventory | Defines the list of managed nodes (`inventory.ini`) |
| Playbooks | YAML files containing automation steps |
| Tasks | Individual actions in playbooks |
| Modules | Built-in functionality (e.g., `apt`, `service`) |
| Roles | Pre-defined reusable automation scripts |

---

## Part A: Ansible Installation

### Step 1: Install Ansible via apt

```bash
sudo apt update -y
sudo apt install ansible -y
ansible --version
```

📸 **Screenshot – Ansible installation via apt and version verification:**

![ansible install](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20144447.png)

---

## Part B: Create Docker Image and Test SSH Login

### Step 1: Generate SSH Key Pair in WSL

```bash
# Generate RSA key pair
ssh-keygen -t rsa -b 4096

# Copy keys to current directory for Docker image build
cp ~/.ssh/id_rsa.pub .
cp ~/.ssh/id_rsa .
```

📸 **Screenshot – SSH key pair generated (RSA 4096):**

![ssh keygen](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20144641.png)

| File | Location | Purpose |
|---|---|---|
| `id_rsa` (Private Key) | Local machine (`~/.ssh/`) | Used to authenticate when connecting — never share |
| `id_rsa.pub` (Public Key) | Remote server (`~/.ssh/authorized_keys`) | Grants access to anyone with matching private key |

---

### Step 2: Create Dockerfile for Ubuntu SSH Server

```dockerfile
FROM ubuntu

RUN apt update -y
RUN apt install -y python3 python3-pip openssh-server
RUN mkdir -p /var/run/sshd

# Configure SSH
RUN mkdir -p /run/sshd && \
    echo 'root:password' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Create .ssh directory
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Copy SSH keys
COPY id_rsa /root/.ssh/id_rsa
COPY id_rsa.pub /root/.ssh/authorized_keys

# Set permissions
RUN chmod 600 /root/.ssh/id_rsa && \
    chmod 644 /root/.ssh/authorized_keys

# Fix SSH login
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

---

### Step 3: Build the Docker Image

```bash
docker build -t ubuntu-server .
```

📸 **Screenshot – Docker image ubuntu-server built successfully (15/15 steps):**

![docker build](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20145055.png)

---

## Part C: Ansible with Docker Exercise

### Step 1: Start 4 Container Servers

```bash
for i in {1..4}; do
  echo -e "\n Creating server${i}\n"
  docker run -d --rm -p 220${i}:22 --name server${i} ubuntu-server
  echo -e "IP of server${i} is $(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server${i})"
done
```

📸 **Screenshot – All 4 server containers started:**

![start servers](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20145115.png)

---

### Step 2: Create Ansible Inventory

```bash
# Get container IPs and build inventory
echo "[servers]" > inventory.ini
for i in {1..4}; do
  docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server${i} >> inventory.ini
done

# Add inventory variables
cat << EOF >> inventory.ini

[servers:vars]
ansible_user=root
ansible_ssh_private_key_file=~/.ssh/id_rsa
ansible_python_interpreter=/usr/bin/python3
EOF
```

---

### Step 3: Review inventory.ini

```bash
cat inventory.ini
```

Expected output:
```ini
[servers]
172.17.0.2
172.17.0.3
172.17.0.4
172.17.0.5

[servers:vars]
ansible_user=root
ansible_ssh_private_key_file=~/.ssh/id_rsa
ansible_python_interpreter=/usr/bin/python3
```

📸 **Screenshot – Container IP addresses retrieved (172.17.0.2 – 172.17.0.5):**

![container ips](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20145313.png)

---

### Step 4: Test SSH Connectivity

```bash
# Manual SSH key-based login test
ssh -i ~/.ssh/id_rsa root@localhost -p 2201
```

📸 **Screenshot – SSH key-based login to server1 successful (Ubuntu 24.04 welcome):**

![ssh login](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151345.png)

```bash
# Ansible ping test across all servers
ansible all -i inventory.ini -m ping
```

📸 **Screenshot – ansible ping SUCCESS on all 4 servers (server1–server4):**

![ansible ping](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151534.png)

---

### Step 5: Create Playbook (playbook.yml)

```yaml
---
- name: Configure servers
  hosts: servers
  become: yes

  tasks:
    - name: Update apt packages
      apt:
        update_cache: yes
        upgrade: dist

    - name: Install packages
      apt:
        name: ["vim", "htop", "wget"]
        state: present

    - name: Create test file
      copy:
        dest: /root/ansible_test.txt
        content: "Configured by Ansible on {{ inventory_hostname }}"
```

---

### Step 6: Run Playbook

```bash
nano playbook.yml
ansible-playbook -i inventory.ini playbook.yml
```

📸 **Screenshot – Playbook execution: Gathering Facts, Update apt, Install packages, Create test file — all servers ok/changed:**

![playbook run](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151847.png)

📸 **Screenshot – PLAY RECAP: server1–server4 all ok=4 changed=2 failed=0:**

![play recap](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151908.png)

---

### Step 7: Verify Changes

```bash
# Verify using Ansible
ansible all -i inventory.ini -m command -a "cat /root/ansible_test.txt"
```

📸 **Screenshot – ansible_test.txt content verified on all servers via Ansible command module:**

![verify ansible](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151923.png)

```bash
# Verify manually via Docker exec
for i in {1..4}; do
  docker exec server${i} cat /root/ansible_test.txt
done
```

📸 **Screenshot – ansible_test.txt verified via docker exec on all 4 containers:**

![verify docker](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151934.png)

---

### Step 8: Cleanup

```bash
for i in {1..4}; do docker rm -f server${i}; done
```

📸 **Screenshot – All 4 server containers removed:**

![cleanup](../LAB-9/SCREENSHOTS/Screenshot%202026-04-11%20151958.png)

---

## Additional Playbook: playbook1.yml

```yaml
---
- name: Configure multiple servers
  hosts: servers
  become: yes

  tasks:
    - name: Update apt package index
      apt:
        update_cache: yes

    - name: Install Python 3 (latest available)
      apt:
        name: python3
        state: latest

    - name: Create test file with content
      copy:
        dest: /root/test_file.txt
        content: |
          This is a test file created by Ansible
          Server name: {{ inventory_hostname }}
          Current date: {{ ansible_date_time.date }}

    - name: Display system information
      command: uname -a
      register: uname_output

    - name: Show disk space
      command: df -h
      register: disk_space

    - name: Print results
      debug:
        msg:
          - "System info: {{ uname_output.stdout }}"
          - "Disk space: {{ disk_space.stdout_lines }}"
```

---

## Workflow Summary

```
1. Generate SSH keys
      ↓
2. Build ubuntu-server Docker image (with SSH configured)
      ↓
3. Launch 4 containers (server1–server4)
      ↓
4. Create inventory.ini with container IPs
      ↓
5. Test SSH + Ansible ping
      ↓
6. Write and run playbook
      ↓
7. Verify changes
      ↓
8. Cleanup containers
```

---

## Key Takeaways

- Ansible is **agentless** — uses SSH, no software needed on managed nodes
- **Idempotent** — running the same playbook multiple times produces the same result
- **Inventory** file maps hostnames/IPs to groups and connection variables
- **Playbooks** define tasks in YAML — human-readable and version-controllable
- Docker containers serve as lightweight stand-ins for real servers in testing
- `ansible -m ping` verifies connectivity before running full playbooks
- `PLAY RECAP` summarizes what changed vs what was already in desired state

---
