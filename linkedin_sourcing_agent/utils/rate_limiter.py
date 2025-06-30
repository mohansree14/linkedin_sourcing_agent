"""
Professional Rate Limiter

Implements sophisticated rate limiting for API calls and web scraping.
Supports multiple rate limiting strategies and backoff mechanisms.

Author: LinkedIn Sourcing Agent Team
Created: June 2025
"""

import asyncio
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from collections import deque
from enum import Enum

from .logging_config import get_logger

logger = get_logger(__name__)


class BackoffStrategy(Enum):
    """Rate limiting backoff strategies"""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


@dataclass
class RateLimitConfig:
    """Rate limiter configuration"""
    max_requests: int = 30
    time_window: int = 60  # seconds
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_backoff: float = 1.0  # seconds
    max_backoff: float = 60.0  # seconds
    retry_after_429: bool = True
    respect_retry_after_header: bool = True


class RateLimiter:
    """
    Professional rate limiter with multiple strategies
    
    Features:
    - Token bucket algorithm for smooth rate limiting
    - Multiple backoff strategies
    - 429 response handling
    - Retry-After header support
    - Per-domain rate limiting
    - Statistics tracking
    """
    
    def __init__(self, 
                 max_requests: int = 30,
                 time_window: int = 60,
                 config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
            config: Optional detailed configuration
        """
        if config:
            self.config = config
        else:
            self.config = RateLimitConfig(
                max_requests=max_requests,
                time_window=time_window
            )
        
        # Token bucket implementation
        self.tokens = self.config.max_requests
        self.last_refill = time.time()
        
        # Request tracking
        self.request_times: deque = deque(maxlen=self.config.max_requests * 2)
        
        # Backoff tracking
        self.consecutive_failures = 0
        self.last_backoff = 0.0
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'backoff_events': 0,
            'avg_wait_time': 0.0
        }
        
        # Per-domain tracking
        self.domain_limiters: Dict[str, 'DomainRateLimiter'] = {}
        
        logger.info(f"Rate limiter initialized: {self.config.max_requests}/{self.config.time_window}s")
    
    async def wait(self, domain: Optional[str] = None) -> None:
        """
        Wait if necessary to respect rate limits
        
        Args:
            domain: Optional domain for per-domain limiting
        """
        start_wait_time = time.time()
        
        # Per-domain rate limiting
        if domain:
            await self._wait_for_domain(domain)
        
        # Global rate limiting
        await self._wait_global()
        
        # Update statistics
        wait_time = time.time() - start_wait_time
        self._update_stats(wait_time)
    
    async def _wait_global(self) -> None:
        """Wait for global rate limit"""
        current_time = time.time()
        
        # Refill tokens based on elapsed time
        time_elapsed = current_time - self.last_refill
        tokens_to_add = time_elapsed * (self.config.max_requests / self.config.time_window)
        self.tokens = min(self.config.max_requests, self.tokens + tokens_to_add)
        self.last_refill = current_time
        
        # Check if we have tokens available
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            self.request_times.append(current_time)
            self.consecutive_failures = 0  # Reset on successful request
            return
        
        # Calculate wait time
        wait_time = (1.0 - self.tokens) * (self.config.time_window / self.config.max_requests)
        
        if wait_time > 0:
            logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
            self.stats['blocked_requests'] += 1
            await asyncio.sleep(wait_time)
            
            # Retry
            await self._wait_global()
    
    async def _wait_for_domain(self, domain: str) -> None:
        """Wait for domain-specific rate limit"""
        if domain not in self.domain_limiters:
            # Create per-domain limiter with more conservative limits
            domain_config = RateLimitConfig(
                max_requests=min(10, self.config.max_requests // 3),
                time_window=self.config.time_window,
                backoff_strategy=self.config.backoff_strategy
            )
            self.domain_limiters[domain] = DomainRateLimiter(domain, domain_config)
        
        await self.domain_limiters[domain].wait()
    
    async def handle_429_response(self, retry_after: Optional[str] = None) -> None:
        """
        Handle 429 Too Many Requests response
        
        Args:
            retry_after: Retry-After header value
        """
        self.consecutive_failures += 1
        
        if retry_after and self.config.respect_retry_after_header:
            try:
                wait_time = float(retry_after)
                logger.warning(f"429 response, waiting {wait_time}s (Retry-After header)")
                await asyncio.sleep(wait_time)
                return
            except ValueError:
                pass
        
        # Calculate backoff time
        wait_time = self._calculate_backoff()
        logger.warning(f"429 response, backing off for {wait_time:.2f}s")
        
        self.stats['backoff_events'] += 1
        await asyncio.sleep(wait_time)
    
    def _calculate_backoff(self) -> float:
        """Calculate backoff time based on strategy"""
        base_time = self.config.initial_backoff
        
        if self.config.backoff_strategy == BackoffStrategy.FIXED:
            backoff = base_time
            
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            backoff = base_time * self.consecutive_failures
            
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            backoff = base_time * (2 ** (self.consecutive_failures - 1))
            
        elif self.config.backoff_strategy == BackoffStrategy.FIBONACCI:
            backoff = base_time * self._fibonacci(self.consecutive_failures)
            
        else:
            backoff = base_time
        
        # Apply jitter and cap
        import random
        jitter = random.uniform(0.8, 1.2)
        backoff = min(backoff * jitter, self.config.max_backoff)
        
        self.last_backoff = backoff
        return backoff
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return 1
        elif n == 2:
            return 2
        
        a, b = 1, 2
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b
    
    def _update_stats(self, wait_time: float) -> None:
        """Update rate limiter statistics"""
        self.stats['total_requests'] += 1
        
        # Update average wait time (exponential moving average)
        alpha = 0.1
        self.stats['avg_wait_time'] = (
            alpha * wait_time + (1 - alpha) * self.stats['avg_wait_time']
        )
    
    def get_stats(self) -> Dict[str, float]:
        """Get rate limiter statistics"""
        stats = self.stats.copy()
        
        # Calculate additional metrics
        if stats['total_requests'] > 0:
            stats['block_rate'] = stats['blocked_requests'] / stats['total_requests']
        else:
            stats['block_rate'] = 0.0
        
        stats['current_tokens'] = self.tokens
        stats['consecutive_failures'] = self.consecutive_failures
        stats['last_backoff'] = self.last_backoff
        
        return stats
    
    def reset(self) -> None:
        """Reset rate limiter state"""
        self.tokens = self.config.max_requests
        self.last_refill = time.time()
        self.request_times.clear()
        self.consecutive_failures = 0
        self.last_backoff = 0.0
        
        # Reset statistics
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'backoff_events': 0,
            'avg_wait_time': 0.0
        }
        
        logger.info("Rate limiter reset")


class DomainRateLimiter:
    """Rate limiter for specific domains"""
    
    def __init__(self, domain: str, config: RateLimitConfig):
        """
        Initialize domain rate limiter
        
        Args:
            domain: Domain name
            config: Rate limit configuration
        """
        self.domain = domain
        self.config = config
        self.tokens = config.max_requests
        self.last_refill = time.time()
        self.request_times: deque = deque(maxlen=config.max_requests * 2)
    
    async def wait(self) -> None:
        """Wait for domain rate limit"""
        current_time = time.time()
        
        # Refill tokens
        time_elapsed = current_time - self.last_refill
        tokens_to_add = time_elapsed * (self.config.max_requests / self.config.time_window)
        self.tokens = min(self.config.max_requests, self.tokens + tokens_to_add)
        self.last_refill = current_time
        
        # Check availability
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            self.request_times.append(current_time)
            return
        
        # Wait
        wait_time = (1.0 - self.tokens) * (self.config.time_window / self.config.max_requests)
        if wait_time > 0:
            logger.debug(f"Domain {self.domain} rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            await self.wait()


# Convenience functions
async def rate_limited_request(rate_limiter: RateLimiter, 
                               request_func,
                               *args, 
                               domain: Optional[str] = None,
                               **kwargs):
    """
    Execute a rate-limited request
    
    Args:
        rate_limiter: Rate limiter instance
        request_func: Function to execute
        *args: Function arguments
        domain: Optional domain for per-domain limiting
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
    """
    await rate_limiter.wait(domain)
    
    try:
        return await request_func(*args, **kwargs)
    except Exception as e:
        # Handle 429 responses
        if hasattr(e, 'status_code') and e.status_code == 429:
            retry_after = getattr(e, 'headers', {}).get('Retry-After')
            await rate_limiter.handle_429_response(retry_after)
            raise
        else:
            raise


def create_rate_limiter(requests_per_minute: int = 30) -> RateLimiter:
    """
    Create a rate limiter with common configuration
    
    Args:
        requests_per_minute: Maximum requests per minute
        
    Returns:
        Configured rate limiter
    """
    return RateLimiter(
        max_requests=requests_per_minute,
        time_window=60
    )
