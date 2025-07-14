"""
Rate limiter for API requests
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple

class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=max_requests))
    
    def is_allowed(self, client_id: str) -> Tuple[bool, float]:
        """
        Check if request is allowed
        
        Args:
            client_id: Identifier for the client (IP, user ID, etc.)
            
        Returns:
            Tuple of (is_allowed, wait_time)
        """
        now = time.time()
        request_history = self.request_history[client_id]
        
        # If we haven't reached max requests yet
        if len(request_history) < self.max_requests:
            request_history.append(now)
            return True, 0
        
        # Check if oldest request is outside time window
        oldest_request = request_history[0]
        if now - oldest_request > self.time_window:
            request_history.append(now)
            return True, 0
        
        # Rate limit exceeded, calculate wait time
        wait_time = self.time_window - (now - oldest_request)
        return False, wait_time
    
    def reset(self, client_id: str):
        """Reset rate limit for a client"""
        if client_id in self.request_history:
            del self.request_history[client_id]

# Global rate limiter instance
GLOBAL_RATE_LIMITER = RateLimiter(max_requests=10, time_window=60)  # 10 requests per minute

def check_rate_limit(client_id: str) -> Tuple[bool, float]:
    """Check if request is allowed based on rate limit"""
    return GLOBAL_RATE_LIMITER.is_allowed(client_id) 