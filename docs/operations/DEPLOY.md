# Deployment Guide

## Quick Deploy Script

Use the automated deploy script:

```bash
./deploy.sh
```

Or manually run the steps:

## Manual Deployment Steps

1. **Stop containers:**
   ```bash
   sudo docker-compose down
   ```

2. **Pull latest code:**
   ```bash
   sudo git pull
   ```

3. **Build without cache (ensures fresh build):**
   ```bash
   sudo docker-compose build --no-cache
   ```

4. **Start containers:**
   ```bash
   sudo docker-compose up -d
   ```

## Verify Deployment

After deployment, verify everything is working:

```bash
# Check container status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f

# Check backend health
curl http://localhost:3399/api/health
```

## Important Notes

- **`--no-cache`** ensures a fresh build, which is important when:
  - Dependencies have changed
  - Service worker configuration has changed
  - You want to ensure users get the latest frontend version

- **Service Worker Updates**: After deployment, users may need to:
  - Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
  - Or wait up to 5 minutes for automatic update detection

## Troubleshooting

If users still see old version:

1. **Check if containers are running:**
   ```bash
   sudo docker-compose ps
   ```

2. **Check frontend logs:**
   ```bash
   sudo docker-compose logs frontend
   ```

3. **Verify service worker files:**
   ```bash
   curl -I http://localhost:3399/sw.js
   ```

4. **Force service worker update** (users can do this):
   - Open DevTools (F12)
   - Application → Service Workers
   - Click "Unregister"
   - Clear site data
   - Reload page

