---
name: Kubernetes Edge Node Deployer
description: Deploys and manages lightweight K8s distributions (e.g., K3s, MicroK8s) on edge hardware for localized processing.
---

# Kubernetes Edge Node Deployer

This skill specializes in deploying "thin" Kubernetes clusters on edge devices, optimizing for resource constraints and unstable network connectivity.

## Workflow

### 1. Perceive (Diagnosis)
- **Hardware Profiling**: Analyze CPU, RAM, and Disk available on the edge node (e.g., Raspberry Pi, Jetson Nano).
- **OS Validation**: Verify the host OS (e.g., Ubuntu Server, Alpine) and kernel compatibility.
- **Connectivity Audit**: Check network latency and stability between the edge node and the central control plane.
- **Resource Constraints**: Identify if the node needs specialized drivers (e.g., GPU/NPU for AI at the edge).

### 2. Plan (Analysis)
- **Distribution Selection**: Choose the right K8s flavor (e.g., `K3s` for low memory, `KubeEdge` for disconnected operation).
- **Networking Model**: Decide between `Flannel` or `Calico` for the CNI based on network complexity.
- **Storage Strategy**: Plan for local persistent volumes (PVs) since network storage is often unavailable at the edge.
- **Deployment Pattern**: Plan for "GitOps" (e.g., FluxCD or ArgoCD) to push updates to the edge.

### 3. Act (Programming)
- **Node Provisioning**: Install the K8s distribution using an automated script or Ansible playbook.
- **Cluster Joining**: Configure the edge node to join the master cluster via a secure token.
- **Resource Quotas**: Set strict `requests` and `limits` for pods to prevent node exhaustion.
- **Edge-Specific Config**: Configure `taints` and `tolerations` to ensure only specific workloads land on edge nodes.
- **Local Registry Setup**: Implement a local container registry to reduce bandwidth usage during updates.

### 4. Evaluate (Verification)
- **Node Health Check**: Verify the node status is `Ready` via `kubectl get nodes`.
- **Pod Scheduling**: Deploy a test workload and confirm it is running on the edge node.
- **Connectivity Test**: Verify the pod can communicate with both the local hardware and the central API.
- **Resource Stress Test**: Monitor memory/CPU under load to ensure the node doesn't crash (OOM).
