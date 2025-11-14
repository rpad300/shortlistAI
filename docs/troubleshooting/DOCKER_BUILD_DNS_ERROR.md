# 🔧 Resolução de Erro de DNS no Docker Build

## ❌ Erro
```
failed to solve: python:3.13-slim: failed to resolve source metadata for docker.io/library/python:3.13-slim: 
failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.13-slim": 
dial tcp: lookup registry-1.docker.io on 127.0.0.53:53: read udp 127.0.0.1:37993->127.0.0.53:53: i/o timeout
```

## 🔍 Causa
O servidor não consegue resolver o DNS para `registry-1.docker.io` (Docker Hub). Isto pode ser:
- Problema de DNS no servidor
- Firewall bloqueando acesso ao Docker Hub
- Problema temporário de rede
- DNS local (127.0.0.53) não está a funcionar corretamente

## ✅ Soluções

### Solução 1: Verificar DNS do Sistema
```bash
# Testar resolução DNS
nslookup registry-1.docker.io
dig registry-1.docker.io

# Se não funcionar, tentar com DNS público
nslookup registry-1.docker.io 8.8.8.8
```

### Solução 2: Configurar DNS no Docker
Criar/editar `/etc/docker/daemon.json`:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
```

Depois reiniciar Docker:
```bash
sudo systemctl restart docker
```

### Solução 3: Usar Mirror do Docker Hub (se disponível)
Se o servidor tiver acesso a um mirror interno, configurar em `/etc/docker/daemon.json`:
```json
{
  "registry-mirrors": ["https://seu-mirror-aqui"]
}
```

### Solução 4: Usar Versão Python Mais Antiga (já em cache)
Se já tiver uma versão mais antiga em cache, pode temporariamente usar:
```dockerfile
FROM python:3.12-slim AS runtime
```
ou
```dockerfile
FROM python:3.11-slim AS runtime
```

**Nota**: Verificar compatibilidade com `requirements.txt` antes de mudar.

### Solução 5: Build Offline (se tiver imagens em cache)
Se já tiver a imagem Python em cache local:
```bash
# Verificar imagens em cache
docker images | grep python

# Se tiver, fazer build sem --no-cache
sudo docker-compose build
```

### Solução 6: Pull Manual da Imagem
Tentar fazer pull manual primeiro:
```bash
# Com DNS alternativo
sudo docker pull python:3.13-slim

# Se funcionar, depois fazer build
sudo docker-compose build
```

### Solução 7: Verificar Conectividade de Rede
```bash
# Testar conectividade
ping registry-1.docker.io
curl -I https://registry-1.docker.io

# Verificar firewall
sudo iptables -L -n | grep docker
```

### Solução 8: Usar Proxy (se necessário)
Se o servidor estiver atrás de um proxy:
```bash
# Configurar proxy para Docker
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
```

Adicionar:
```ini
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1"
```

Depois:
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 🎯 Solução Rápida Recomendada

1. **Configurar DNS no Docker** (Solução 2) - Mais provável de resolver
2. **Verificar conectividade** (Solução 7) - Diagnosticar problema
3. **Se urgente**: Usar versão Python mais antiga temporariamente (Solução 4)

## 📝 Notas

- O erro `127.0.0.53:53` indica que o sistema está a usar systemd-resolved como DNS
- Se o problema persistir, pode ser necessário contactar o administrador de rede
- Em alguns casos, o problema resolve-se sozinho após alguns minutos (problema temporário de rede)

