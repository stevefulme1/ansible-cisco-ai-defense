"""Poll Cisco AI Defense for alert events."""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None


def _validate_host(host: str) -> bool:
    """Validate host parameter to prevent SSRF."""
    import re

    if "://" in host:
        logger.error(
            "Host parameter must not include a URL scheme (got '%s'). "
            "Provide only the hostname, e.g. 'defense.cisco.com'.",
            host,
        )
        return False

    if re.search(r'[/?#@]', host):
        logger.error("Host parameter contains invalid characters: %s", host)
        return False

    return True


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Poll Cisco AI Defense for events and push them to the queue."""
    host = args["host"]

    if not _validate_host(host):
        logger.error("Host validation failed - event source will not start.")
        return

    interval = int(args.get("interval", 60))
    api_key = args.get("api_key", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    seen = set()
    while True:
        try:
            resp = requests.get(
                f"https://{host}/api/v1/alerts",
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                item_id = str(item.get("id", ""))
                if item_id and item_id not in seen:
                    seen.add(item_id)
                    await queue.put(dict([("cisco_ai_defense", item)]))
        except Exception as exc:
            logger.error("Error polling: %s", exc)
        await asyncio.sleep(interval)
