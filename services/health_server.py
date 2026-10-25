"""Render va boshqa hostinglar uchun health-check serveri.

Bot polling rejimida ishlaydi, lekin Render bepul tarifi faqat port
tinglaydigan web-service'ni qabul qiladi. Shu sababli PORT o'rnatilgan
bo'lsa, kichik HTTP server ham ishga tushadi.
"""

from __future__ import annotations

import logging
import os

from aiohttp import web

logger = logging.getLogger(__name__)

SERVICE_NAME = "ustozai-bot"


async def _health(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "commit": os.getenv("RENDER_GIT_COMMIT", "local")[:12],
        }
    )


async def _root(request: web.Request) -> web.Response:
    return web.Response(
        text=(
            "UstozAI bot ishlayapti.\n"
            "Telegramda botni ochib /start buyrug'ini yuboring."
        ),
        content_type="text/plain",
    )


def _read_port() -> int | None:
    raw = os.getenv("PORT", "").strip()
    if not raw:
        return None
    try:
        port = int(raw)
    except ValueError:
        logger.warning("PORT noto'g'ri qiymatga ega: %r. Server ochilmadi.", raw)
        return None
    if not 1 <= port <= 65535:
        logger.warning("PORT 1-65535 oralig'ida bo'lishi kerak: %s", port)
        return None
    return port


async def start_health_server() -> web.AppRunner | None:
    """PORT berilgan bo'lsa HTTP health serverini ishga tushiradi."""
    port = _read_port()
    if port is None:
        return None

    app = web.Application()
    app.router.add_get("/", _root)
    app.router.add_get("/health", _health)
    app.router.add_get("/healthz", _health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server 0.0.0.0:%s manzilida ishga tushdi.", port)
    return runner


async def stop_health_server(runner: web.AppRunner | None) -> None:
    if runner is not None:
        await runner.cleanup()
        logger.info("Health server to'xtatildi.")
