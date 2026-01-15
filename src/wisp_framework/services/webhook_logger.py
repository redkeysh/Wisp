"""Rate-limited webhook logger service with retry logic."""

import asyncio
import logging
import time
from typing import Any, List, Optional

import aiohttp

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class WebhookLoggerService(BaseService):
    """Service for sending logs to Discord webhooks with rate limiting."""

    def __init__(self, config: Any) -> None:
        """Initialize the webhook logger service."""
        super().__init__(config)
        self._webhook_url: Optional[str] = config.webhook_logger_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = 1.0  # Minimum delay between requests
        self._last_request_time = 0.0
        self._queue: List[dict[str, Any]] = []
        self._max_retries = 3
        self._retry_delay = 1.0

    async def startup(self) -> None:
        """Start up the webhook logger service."""
        if self._webhook_url:
            self._session = aiohttp.ClientSession()
            logger.info("Webhook logger service started")
        else:
            logger.info("Webhook logger service started (no webhook URL configured)")
        self._mark_initialized()

    async def shutdown(self) -> None:
        """Shut down the webhook logger service."""
        # Send any queued messages
        if self._queue:
            logger.info(f"Sending {len(self._queue)} queued webhook messages...")
            for message in self._queue:
                await self._send_message(message)
            self._queue.clear()

        if self._session:
            await self._session.close()
            self._session = None
        logger.info("Webhook logger service shut down")

    async def send_embed(self, embed: dict[str, Any]) -> None:
        """Send an embed to the webhook."""
        if not self._webhook_url or not self._session:
            return

        message = {"embeds": [embed]}
        await self._send_message(message)

    async def send_embeds(self, embeds: List[dict[str, Any]]) -> None:
        """Send multiple embeds to the webhook (max 10 per message)."""
        if not self._webhook_url or not self._session:
            return

        # Discord allows max 10 embeds per message
        for i in range(0, len(embeds), 10):
            batch = embeds[i : i + 10]
            message = {"embeds": batch}
            await self._send_message(message)

    async def _send_message(self, message: dict[str, Any]) -> None:
        """Send a message to the webhook with rate limiting and retry logic."""
        if not self._webhook_url or not self._session:
            return

        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - time_since_last)

        # Retry logic with exponential backoff
        for attempt in range(self._max_retries):
            try:
                async with self._session.post(
                    self._webhook_url, json=message
                ) as response:
                    if response.status == 204:
                        self._last_request_time = time.time()
                        return
                    elif response.status == 429:
                        # Rate limited - wait and retry
                        retry_after = float(response.headers.get("Retry-After", 5))
                        logger.warning(
                            f"Webhook rate limited, waiting {retry_after}s"
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response_text = await response.text()
                        logger.error(
                            f"Webhook request failed: {response.status} - {response_text}"
                        )
                        if attempt < self._max_retries - 1:
                            await asyncio.sleep(
                                self._retry_delay * (2 ** attempt)
                            )
                            continue
                        return

            except Exception as e:
                logger.error(f"Webhook request error: {e}", exc_info=True)
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                    continue
                return
