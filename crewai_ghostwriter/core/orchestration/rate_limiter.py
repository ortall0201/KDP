"""
Rate Limiter for API call throttling.
Prevents exceeding API rate limits (e.g., 30 RPM for OpenAI).
"""

import asyncio
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Supports multiple rate limits:
    - Requests per minute (RPM)
    - Requests per day (RPD)
    - Concurrent requests limit
    """

    def __init__(
        self,
        max_requests_per_minute: int = 30,
        max_requests_per_day: Optional[int] = None,
        max_concurrent: int = 5
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Max requests per minute (default: 30)
            max_requests_per_day: Max requests per day (optional)
            max_concurrent: Max concurrent requests (default: 5)
        """
        self.max_rpm = max_requests_per_minute
        self.max_rpd = max_requests_per_day
        self.max_concurrent = max_concurrent

        # Track request timestamps
        self.requests_minute = deque()  # Last minute of requests
        self.requests_day = deque()  # Last day of requests

        # Semaphore for concurrent limit
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Lock for thread safety
        self.lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquire permission to make a request.
        Blocks until rate limit allows the request.
        """
        async with self.lock:
            now = time.time()

            # Wait for RPM limit
            await self._wait_for_rpm(now)

            # Wait for RPD limit (if set)
            if self.max_rpd:
                await self._wait_for_rpd(now)

            # Record this request
            self.requests_minute.append(now)
            if self.max_rpd:
                self.requests_day.append(now)

        # Acquire concurrent slot (will block if at max_concurrent)
        await self.semaphore.acquire()

    def release(self):
        """Release the concurrent slot."""
        self.semaphore.release()

    async def _wait_for_rpm(self, now: float):
        """Wait if we've exceeded requests per minute."""
        # Remove requests older than 1 minute
        one_minute_ago = now - 60
        while self.requests_minute and self.requests_minute[0] < one_minute_ago:
            self.requests_minute.popleft()

        # If at limit, wait until oldest request expires
        if len(self.requests_minute) >= self.max_rpm:
            oldest = self.requests_minute[0]
            wait_time = 60 - (now - oldest) + 0.1  # Add 0.1s buffer
            if wait_time > 0:
                print(f"⏳ Rate limit: waiting {wait_time:.1f}s (RPM: {self.max_rpm})")
                await asyncio.sleep(wait_time)

    async def _wait_for_rpd(self, now: float):
        """Wait if we've exceeded requests per day."""
        # Remove requests older than 1 day
        one_day_ago = now - 86400
        while self.requests_day and self.requests_day[0] < one_day_ago:
            self.requests_day.popleft()

        # If at limit, wait until oldest request expires
        if len(self.requests_day) >= self.max_rpd:
            oldest = self.requests_day[0]
            wait_time = 86400 - (now - oldest) + 1  # Add 1s buffer
            if wait_time > 0:
                hours = wait_time / 3600
                print(f"⏳ Daily rate limit: waiting {hours:.1f}h (RPD: {self.max_rpd})")
                await asyncio.sleep(wait_time)

    def get_stats(self) -> Dict[str, int]:
        """
        Get current rate limiter statistics.

        Returns:
            Dictionary with current usage stats
        """
        now = time.time()

        # Count requests in last minute
        one_minute_ago = now - 60
        rpm_count = sum(1 for t in self.requests_minute if t > one_minute_ago)

        # Count requests in last day
        rpd_count = 0
        if self.max_rpd:
            one_day_ago = now - 86400
            rpd_count = sum(1 for t in self.requests_day if t > one_day_ago)

        return {
            "requests_last_minute": rpm_count,
            "rpm_limit": self.max_rpm,
            "rpm_available": max(0, self.max_rpm - rpm_count),
            "requests_last_day": rpd_count,
            "rpd_limit": self.max_rpd or 0,
            "rpd_available": max(0, (self.max_rpd or 0) - rpd_count),
            "concurrent_limit": self.max_concurrent,
            "concurrent_available": self.semaphore._value
        }


class MultiProviderRateLimiter:
    """
    Rate limiter that handles multiple API providers.

    Each provider (OpenAI, Anthropic) has its own limits.
    """

    def __init__(self):
        """Initialize with default provider limits."""
        self.limiters = {
            "openai": RateLimiter(
                max_requests_per_minute=30,
                max_concurrent=5
            ),
            "anthropic": RateLimiter(
                max_requests_per_minute=50,
                max_concurrent=5
            ),
            "default": RateLimiter(
                max_requests_per_minute=30,
                max_concurrent=5
            )
        }

    async def acquire(self, provider: str = "default"):
        """
        Acquire permission for a specific provider.

        Args:
            provider: API provider name ("openai", "anthropic", "default")
        """
        limiter = self.limiters.get(provider, self.limiters["default"])
        await limiter.acquire()

    def release(self, provider: str = "default"):
        """
        Release permission for a specific provider.

        Args:
            provider: API provider name
        """
        limiter = self.limiters.get(provider, self.limiters["default"])
        limiter.release()

    def get_all_stats(self) -> Dict[str, Dict]:
        """
        Get stats for all providers.

        Returns:
            Dictionary mapping provider names to their stats
        """
        return {
            provider: limiter.get_stats()
            for provider, limiter in self.limiters.items()
        }


class RateLimitedTask:
    """
    Context manager for rate-limited task execution.

    Usage:
        async with RateLimitedTask(rate_limiter, "openai"):
            result = await expensive_api_call()
    """

    def __init__(self, rate_limiter: RateLimiter, provider: str = "default"):
        """
        Initialize rate-limited task.

        Args:
            rate_limiter: RateLimiter or MultiProviderRateLimiter instance
            provider: API provider name (for MultiProviderRateLimiter)
        """
        self.rate_limiter = rate_limiter
        self.provider = provider

    async def __aenter__(self):
        """Acquire rate limit permission."""
        if isinstance(self.rate_limiter, MultiProviderRateLimiter):
            await self.rate_limiter.acquire(self.provider)
        else:
            await self.rate_limiter.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release rate limit permission."""
        if isinstance(self.rate_limiter, MultiProviderRateLimiter):
            self.rate_limiter.release(self.provider)
        else:
            self.rate_limiter.release()
        return False
