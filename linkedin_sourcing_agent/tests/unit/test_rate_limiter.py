"""
Unit tests for rate limiter
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch

from linkedin_sourcing_agent.utils.rate_limiter import RateLimiter, RateLimitError


class TestRateLimiter:
    """Test cases for RateLimiter"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_init(self):
        """Test RateLimiter initialization"""
        limiter = RateLimiter(max_requests=10, time_window_seconds=60)
        
        assert limiter.max_requests == 10
        assert limiter.time_window_seconds == 60
        assert len(limiter.request_times) == 0
    
    @pytest.mark.asyncio
    async def test_acquire_within_limit(self):
        """Test acquiring tokens within rate limit"""
        limiter = RateLimiter(max_requests=5, time_window_seconds=60)
        
        # Should allow requests within limit
        for i in range(5):
            await limiter.acquire()
        
        assert len(limiter.request_times) == 5
    
    @pytest.mark.asyncio
    async def test_acquire_exceeds_limit(self):
        """Test behavior when exceeding rate limit"""
        limiter = RateLimiter(max_requests=2, time_window_seconds=1)
        
        # First two requests should pass immediately
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        first_requests_time = time.time() - start_time
        
        # Should be very fast (< 0.1 seconds)
        assert first_requests_time < 0.1
        
        # Third request should be delayed
        start_time = time.time()
        await limiter.acquire()
        third_request_time = time.time() - start_time
        
        # Should be delayed by at least some time (but less than full window)
        assert third_request_time > 0.01  # Some delay expected
    
    @pytest.mark.asyncio
    async def test_cleanup_old_requests(self):
        """Test cleanup of old request timestamps"""
        limiter = RateLimiter(max_requests=5, time_window_seconds=1)
        
        # Add some requests
        await limiter.acquire()
        await limiter.acquire()
        
        assert len(limiter.request_times) == 2
        
        # Wait for time window to pass
        await asyncio.sleep(1.1)
        
        # Next request should clean up old ones
        await limiter.acquire()
        
        # Should only have the latest request
        assert len(limiter.request_times) == 1
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test RateLimiter as async context manager"""
        limiter = RateLimiter(max_requests=5, time_window_seconds=60)
        
        async with limiter:
            # Should have acquired a token
            assert len(limiter.request_times) == 1
        
        # Should still have the recorded request time
        assert len(limiter.request_times) == 1
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """Test multiple concurrent requests"""
        limiter = RateLimiter(max_requests=3, time_window_seconds=1)
        
        # Start multiple concurrent requests
        tasks = []
        for i in range(5):
            task = asyncio.create_task(limiter.acquire())
            tasks.append(task)
        
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Should take some time due to rate limiting
        assert total_time > 0.5  # At least some delay expected
        assert len(limiter.request_times) == 5
    
    @pytest.mark.asyncio
    async def test_zero_max_requests_raises_error(self):
        """Test that zero max_requests raises appropriate error"""
        with pytest.raises(ValueError):
            RateLimiter(max_requests=0, time_window_seconds=60)
    
    @pytest.mark.asyncio
    async def test_negative_time_window_raises_error(self):
        """Test that negative time window raises appropriate error"""
        with pytest.raises(ValueError):
            RateLimiter(max_requests=10, time_window_seconds=-1)
    
    @pytest.mark.asyncio
    async def test_get_current_usage(self):
        """Test getting current usage statistics"""
        limiter = RateLimiter(max_requests=10, time_window_seconds=60)
        
        # Initially should be empty
        usage = limiter.get_current_usage()
        assert usage['current_requests'] == 0
        assert usage['max_requests'] == 10
        assert usage['time_window_seconds'] == 60
        assert usage['usage_percentage'] == 0.0
        
        # Add some requests
        await limiter.acquire()
        await limiter.acquire()
        
        usage = limiter.get_current_usage()
        assert usage['current_requests'] == 2
        assert usage['usage_percentage'] == 20.0
    
    @pytest.mark.asyncio
    async def test_reset(self):
        """Test resetting the rate limiter"""
        limiter = RateLimiter(max_requests=5, time_window_seconds=60)
        
        # Add some requests
        await limiter.acquire()
        await limiter.acquire()
        
        assert len(limiter.request_times) == 2
        
        # Reset
        limiter.reset()
        
        assert len(limiter.request_times) == 0
    
    @pytest.mark.asyncio
    async def test_can_make_request(self):
        """Test checking if request can be made without actually making it"""
        limiter = RateLimiter(max_requests=2, time_window_seconds=60)
        
        # Initially should be able to make requests
        assert limiter.can_make_request() is True
        
        # Add requests up to limit
        await limiter.acquire()
        assert limiter.can_make_request() is True
        
        await limiter.acquire()
        assert limiter.can_make_request() is False
    
    @pytest.mark.asyncio
    async def test_wait_time_calculation(self):
        """Test calculation of wait time"""
        limiter = RateLimiter(max_requests=1, time_window_seconds=2)
        
        # First request should have no wait time
        wait_time = limiter.get_wait_time()
        assert wait_time == 0
        
        # After first request, should need to wait
        await limiter.acquire()
        wait_time = limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 2  # Should not exceed time window
    
    @pytest.mark.asyncio 
    async def test_burst_handling(self):
        """Test handling of burst requests"""
        limiter = RateLimiter(max_requests=3, time_window_seconds=1)
        
        # Send burst of requests
        start_time = time.time()
        
        # These should go through quickly
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()
        
        burst_time = time.time() - start_time
        assert burst_time < 0.1  # Should be very fast
        
        # Next requests should be rate limited
        start_time = time.time()
        await limiter.acquire()
        delayed_time = time.time() - start_time
        
        assert delayed_time > 0.05  # Should have some delay


if __name__ == '__main__':
    pytest.main([__file__])
