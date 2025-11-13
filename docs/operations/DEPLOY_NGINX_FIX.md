# 🔧 Fix 413 Error - Deploy Nginx Configuration Update

## Problema
O erro **413 Request Entity Too Large** acontece porque o nginx em produção ainda tem o limite padrão de 1MB, mas o código já foi atualizado no GitHub com `client_max_body_size 50M`.

## Solução: Reconstruir Container Frontend

### Opção 1: Se estás a usar Docker Compose em produção

```bash
# 1. Fazer pull do código mais recente
git pull origin main

# 2. Reconstruir o container frontend
docker compose build frontend

# 3. Reiniciar o container frontend
docker compose up -d frontend

# 4. Verificar logs
docker compose logs -f frontend
```

### Opção 2: Se estás a usar Docker diretamente

```bash
# 1. Fazer pull do código mais recente
git pull origin main

# 2. Ir para o diretório do frontend
cd src/frontend

# 3. Reconstruir a imagem
docker build -t shortlistai-frontend:latest .

# 4. Parar o container atual
docker stop shortlistai-frontend

# 5. Remover o container antigo
docker rm shortlistai-frontend

# 6. Iniciar o novo container
docker run -d \
  --name shortlistai-frontend \
  -p 80:80 \
  --restart unless-stopped \
  shortlistai-frontend:latest

# 7. Verificar logs
docker logs -f shortlistai-frontend
```

### Opção 3: Se tens nginx externo (fora do Docker)

Se o nginx está a correr diretamente no servidor (não dentro do Docker), precisas de atualizar a configuração manualmente:

1. Editar o ficheiro de configuração do nginx (geralmente em `/etc/nginx/sites-available/default` ou `/etc/nginx/nginx.conf`)

2. Adicionar ou atualizar estas linhas no bloco `server` ou `http`:

```nginx
client_max_body_size 50M;
client_body_buffer_size 128k;
```

3. No bloco `location /api/` (ou onde está o proxy_pass), adicionar:

```nginx
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_request_buffering off;
proxy_buffering off;
```

4. Testar a configuração:
```bash
sudo nginx -t
```

5. Recarregar o nginx:
```bash
sudo systemctl reload nginx
# ou
sudo service nginx reload
```

## Verificação

Após o deploy, verifica se funcionou:

1. Tenta fazer upload de 2-3 CVs no step5
2. Se ainda der erro 413, verifica os logs do nginx:
   ```bash
   docker compose logs frontend | grep nginx
   # ou
   sudo tail -f /var/log/nginx/error.log
   ```

## O que foi alterado

O ficheiro `src/frontend/docker/nginx.conf` foi atualizado com:
- `client_max_body_size 50M;` (antes era 1MB padrão)
- `client_body_buffer_size 128k;`
- Timeouts aumentados para 300s
- Buffering desativado para melhor performance

## Nota Importante

O erro 500 no step6/step7 acontece porque o step5 falhou (413). Após corrigir o nginx e fazer upload com sucesso, os erros 500 devem desaparecer.

