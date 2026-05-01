# Experiment 12: Container Orchestration using Kubernetes

---

## Objective

Learn why Kubernetes is used, its basic concepts, and how to deploy, scale, and self-heal applications using Kubernetes commands.

---

## Theory

### Why Kubernetes over Docker Swarm?

| Reason | Explanation |
|---|---|
| Industry standard | Most companies use Kubernetes |
| Powerful scheduling | Automatically decides where to run your app |
| Large ecosystem | Many tools and plugins available |
| Cloud-native support | Works on AWS, Google Cloud, Azure, etc. |

### Core Kubernetes Concepts

| Docker Concept | Kubernetes Equivalent | What it means |
|---|---|---|
| Container | Pod | Smallest unit in K8s — a group of one or more containers |
| Compose service | Deployment | Describes how your app should run (image, replicas, etc.) |
| Load balancing | Service | Exposes your app to the outside world or other pods |
| Scaling | ReplicaSet | Ensures a certain number of pod copies are always running |

---

## Part A: Hands-On Lab (using kind)

### Setup: Create a Cluster

```bash
kind create cluster
kubectl get nodes
```

📸 **Screenshot – kind create cluster completed and kubectl get nodes showing kind-control-plane:**

![kind cluster](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20092347.png)

---

### Task 1: Create a Deployment

**`wordpress-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wordpress
  template:
    metadata:
      labels:
        app: wordpress
    spec:
      containers:
      - name: wordpress
        image: wordpress:latest
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f wordpress-deployment.yaml
```

---

### Task 2: Expose the Deployment as a Service

**`wordpress-service.yaml`:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress-service
spec:
  type: NodePort
  selector:
    app: wordpress
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30007
```

```bash
kubectl apply -f wordpress-service.yaml
```

---

### Task 3: Access WordPress via Port-Forward

Since kind runs inside Docker, use port-forward to access the service locally:

```bash
kubectl port-forward service/wordpress-service 8080:80
```

📸 **Screenshot – kubectl port-forward forwarding localhost:8080 to wordpress-service port 80:**

![port forward](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20092548.png)

Open `http://localhost:8080` in your browser:

📸 **Screenshot – Browser at localhost:8080 (DB connection error — WordPress pod running without a database):**

![wordpress browser](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20092613.png)

---

### Task 4: Scale the Deployment

```bash
kubectl scale deployment wordpress --replicas=4
kubectl get pods
```

📸 **Screenshot – kubectl scale to 4 replicas and kubectl get pods showing 4 Running pods:**

![scale pods](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20092728.png)

---

### Task 5: Self-Healing Demonstration

```bash
# Get pod names
kubectl get pods

# Delete one pod
kubectl delete pod <pod-name>

# Check pods again
kubectl get pods
```

📸 **Screenshot – kubectl get pods (4 running), kubectl delete pod, kubectl get pods (4 still running with new replacement):**

![self healing](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20092920.png)

> **Why?** The Deployment ensures the desired replica count (4) is always maintained — deleting a pod immediately triggers a replacement.

---

### Task 6: Cleanup

```bash
kubectl delete -f wordpress-deployment.yaml
kubectl delete -f wordpress-service.yaml
```

📸 **Screenshot – kubectl delete removing deployment and service:**

![cleanup](../LAB-12/SCREENSHOTS/Screenshot%202026-05-01%20093131.png)

---

## Part B: Swarm vs Kubernetes Comparison

| Feature | Docker Swarm | Kubernetes |
|---|---|---|
| Setup | Very easy | More complex |
| Scaling | Basic | Advanced (auto-scaling) |
| Ecosystem | Small | Huge |
| Industry use | Rare | Standard |

**Verdict:** Learn Kubernetes — it's what companies use.

---

## Part C: Advanced Lab — Real Cluster with kubeadm

### Lab Requirements

- 2 or 3 VMs (VirtualBox / VMware), Ubuntu 22.04 or 24.04
- Each VM: 2+ CPU, 2+ GB RAM

### Step 1: Install kubeadm, kubelet, kubectl on all nodes

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubeadm kubelet kubectl
sudo apt-mark hold kubeadm kubelet kubectl
```

### Step 2: Initialize Control Plane (Master only)

```bash
sudo kubeadm init
```

### Step 3: Set up kubeconfig

```bash
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl get nodes
```

### Step 4: Install Network Plugin (Calico)

```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

### Step 5: Join Worker Nodes

Run the join command shown after `kubeadm init` on each worker:

```bash
kubeadm join 192.168.1.100:6443 --token abcdef.0123456789abcdef \
    --discovery-token-ca-cert-hash sha256:...
```

### Step 6: Verify the Full Cluster

```bash
kubectl get nodes
```

Expected output:
```
NAME      STATUS   ROLES           AGE   VERSION
master    Ready    control-plane   5m    v1.29.0
worker1   Ready    <none>          2m    v1.29.0
worker2   Ready    <none>          2m    v1.29.0
```

---

## Summary

| You started with | You can now do |
|---|---|
| Single container (`docker run`) | Multi-container (Compose) |
| Manual scaling | One-command scaling (`kubectl scale`) |
| Manual recovery | Automatic self-healing |
| Single host | Multi-host cluster |

---

## Commands Cheat Sheet

| Goal | Command |
|---|---|
| Apply a YAML file | `kubectl apply -f file.yaml` |
| See all pods | `kubectl get pods` |
| See all services | `kubectl get svc` |
| Scale a deployment | `kubectl scale deployment <name> --replicas=N` |
| Port-forward a service | `kubectl port-forward service/<name> <local>:<remote>` |
| Delete a pod | `kubectl delete pod <pod-name>` |
| Delete by file | `kubectl delete -f file.yaml` |
| See all nodes | `kubectl get nodes` |

---

## Tool Selection Guide

| Tool | Best for |
|---|---|
| kind | Quick learning on your laptop |
| Minikube | Single-node cluster testing |
| kubeadm | Real, production-style cluster |

---
