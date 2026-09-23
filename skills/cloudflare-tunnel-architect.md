---
name: Cloudflare Tunnel Architect
description: Designs and implements secure, zero-trust connectivity between local infrastructure and the Cloudflare Edge.
---

# Cloudflare Tunnel Architect

This skill eliminates the need for open inbound ports by utilizing `cloudflared` to create secure, authenticated tunnels to internal services.

## Workflow

### 1. Perceive (Diagnosis)
- **Network Mapping**: Identify internal services (IPs, ports) that need public exposure.
- **Current Security Audit**: Analyze existing firewall rules and open ports (e.g., port 80/443/22).
- **Environment Check**: Determine where `cloudflared` will reside (Docker, Linux VM, Kubernetes).
- **Traffic Analysis**: Determine the expected traffic volume and required protocol support (HTTP, TCP, SSH).

### 2. Plan (Analysis)
- **Tunnel Topology**: Decide between a single tunnel with multiple ingress rules or multiple tunnels for isolation.
- **Zero Trust Integration**: Plan the Access policies (e.g., email-based auth, GitHub group membership) for each service.
- **DNS Mapping**: Map internal services to public CNAMEs via the Cloudflare dashboard or API.
- **Failover Strategy**: Design redundant tunnels across different availability zones.

### 3. Act (Programming)
- **Tunnel Creation**: Provision the tunnel using `cloudflared tunnel create`.
- **Configuration Authoring**: Write the `config.yml` specifying ingress rules and origin services.
- **Deployment**: Install and run `cloudflared` as a systemd service or Docker container.
- **DNS Routing**: Link the tunnel to the DNS zone via `cloudflared tunnel route dns`.
- **Access Policy Setup**: Configure Cloudflare Access rules to protect the tunnel endpoints.

### 4. Evaluate (Verification)
- **Connectivity Test**: Verify the service is reachable via the public URL.
- **Auth Validation**: Ensure that unauthenticated requests are intercepted by the Cloudflare Access page.
- **Log Audit**: Check `cloudflared` logs for connection stability and errors.
- **Security Scan**: Verify that the origin server no longer has public inbound ports open.
