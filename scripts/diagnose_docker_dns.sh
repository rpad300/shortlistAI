#!/bin/bash
# Script de diagnóstico para problemas de DNS do Docker

echo "🔍 Diagnóstico de DNS do Docker"
echo "================================"
echo ""

echo "1. Testando resolução DNS do sistema..."
nslookup registry-1.docker.io
echo ""

echo "2. Testando com DNS público (8.8.8.8)..."
nslookup registry-1.docker.io 8.8.8.8
echo ""

echo "3. Testando conectividade HTTP..."
curl -I --max-time 5 https://registry-1.docker.io/v2/ 2>&1 | head -5
echo ""

echo "4. Verificando configuração DNS do Docker..."
if [ -f /etc/docker/daemon.json ]; then
    echo "Arquivo /etc/docker/daemon.json existe:"
    cat /etc/docker/daemon.json
else
    echo "Arquivo /etc/docker/daemon.json NÃO existe"
fi
echo ""

echo "5. Verificando DNS do sistema..."
cat /etc/resolv.conf
echo ""

echo "6. Verificando imagens Python em cache..."
docker images | grep python || echo "Nenhuma imagem Python em cache"
echo ""

echo "7. Testando pull manual da imagem..."
docker pull python:3.13-slim 2>&1 | head -10
echo ""

echo "✅ Diagnóstico completo!"
echo ""
echo "📝 Próximos passos:"
echo "   - Se DNS não resolver: Configurar DNS no Docker (ver docs/troubleshooting/DOCKER_BUILD_DNS_ERROR.md)"
echo "   - Se conectividade falhar: Verificar firewall/proxy"
echo "   - Se pull funcionar: Fazer build normalmente"

