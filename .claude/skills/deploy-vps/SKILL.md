---
name: deploy-vps
description: Deploy apps to Hostinger VPS, check status, rollback, and manage the production environment. Use after merging PRs, when checking deployment health, or for manual deploys and rollbacks.
allowed-tools: Bash(ssh *), Bash(gh *), Bash(docker *), Bash(git *), Bash(curl *)
---

## VPS Deployment Workflow

### Architecture
- **VPS**: `72.60.187.119` (SSH as root)
- **Reverse proxy**: Traefik at `/root/infra/` (ports 80/443, auto TLS)
- **Apps directory**: `/root/apps/`

### Apps

| App | VPS Path | Compose File | Image Source | URL |
|-----|----------|-------------|--------------|-----|
| stock-ranker | `/root/apps/stock-ranker/` | `docker-compose.prod.yml` | `ghcr.io/yarin-claude-code/stocks/{backend,frontend}:main` | `https://stocks.srv1030125.hstgr.cloud` |
| pinecone-rag | `/root/apps/pinecone-rag/` | `docker-compose.prod.yml` | `ghcr.io/yarin-claude-code/pinecone-rag:master` | `https://rag.srv1030125.hstgr.cloud` |
| n8n | `/root/infra/` (in Traefik compose) | `docker-compose.yml` | `docker.n8n.io/n8nio/n8n:latest` | Behind Traefik |

---

### 1. Check deployment status
```bash
ssh root@72.60.187.119 "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"
```

### 2. Check health of all apps
```bash
ssh root@72.60.187.119 "docker inspect --format '{{.Name}}: {{.State.Health.Status}}' \$(docker ps -q) 2>/dev/null || echo 'No health checks configured on some containers'"
```

### 3. Deploy stock-ranker (manual)
```bash
ssh root@72.60.187.119 "cd /root/apps/stock-ranker && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d --remove-orphans && docker image prune -f"
```

### 4. Deploy pinecone-rag (manual)
```bash
ssh root@72.60.187.119 "cd /root/apps/pinecone-rag && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d --remove-orphans && docker image prune -f"
```

### 5. Rollback stock-ranker to specific SHA
Replace `SHA` with the short git commit hash:
```bash
ssh root@72.60.187.119 "cd /root/apps/stock-ranker && sed -i 's/:main/:sha-SHA/g' docker-compose.prod.yml && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d"
```

### 6. Rollback pinecone-rag to specific SHA
```bash
ssh root@72.60.187.119 "cd /root/apps/pinecone-rag && sed -i 's/:master/:sha-SHA/g' docker-compose.prod.yml && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d"
```

### 7. View logs
```bash
ssh root@72.60.187.119 "docker logs --tail 50 stock-ranker-backend"
ssh root@72.60.187.119 "docker logs --tail 50 stock-ranker-frontend"
ssh root@72.60.187.119 "docker logs --tail 50 pinecone-rag"
```

### 8. Check CI/CD pipeline status
```bash
gh run list --repo yarin-claude-code/stocks --limit 5
gh run list --repo yarin-claude-code/pinecone-rag --limit 5
```

### 9. VPS maintenance
```bash
# Disk usage
ssh root@72.60.187.119 "df -h / && echo && docker system df"

# Manual prune
ssh root@72.60.187.119 "docker system prune -af --filter 'until=168h'"

# Check backups
ssh root@72.60.187.119 "ls -lh /root/backups/"

# Check crontab
ssh root@72.60.187.119 "crontab -l"
```

### 10. Restart Traefik/infra
```bash
ssh root@72.60.187.119 "cd /root/infra && docker compose down && docker compose up -d"
```

---

### CI/CD Flow (automatic)
1. Push to `main` (stocks) or `master` (rag) triggers GitHub Actions
2. CI: lint → test → build Docker image → push to GHCR
3. CD: SSH into VPS → `docker compose pull` → `docker compose up -d`
4. Health checks auto-restart unhealthy containers

### GitHub Secrets (both repos)
- `VPS_HOST`: 72.60.187.119
- `VPS_USER`: root
- `VPS_SSH_KEY`: ed25519 private key
