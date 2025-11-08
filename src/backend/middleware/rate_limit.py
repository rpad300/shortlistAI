"""
Rate limiting middleware to prevent abuse.

Implements rate limiting on public endpoints.
"""

from fastapi import Request, HTTPException
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, use Redis or similar distributed cache.
    """
    
    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per IP per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.now()
    
    def _cleanup_old_requests(self):
        """Remove old request timestamps."""
        now = datetime.now()
        if now - self.last_cleanup > self.cleanup_interval:
            cutoff = now - timedelta(minutes=1)
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    ts for ts in self.requests[ip]
                    if ts > cutoff
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = now
    
    async def check_rate_limit(self, request: Request):
        """
        Check if request should be rate limited.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException if rate limit exceeded
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for localhost in development
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            return
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Get current time
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Get requests for this IP in the last minute
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if ts > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Add current request
        self.requests[client_ip].append(now)


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        from config import settings
        _rate_limiter = RateLimiter(settings.rate_limit_per_minute)
    return _rate_limiter

