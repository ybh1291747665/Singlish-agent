import asyncio
import sys

_worker_event_loop: asyncio.AbstractEventLoop | None = None


def configure_worker_event_loop() -> None:
    if sys.platform != "win32":
        return

    selector_policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if selector_policy is None:
        return

    current_policy = asyncio.get_event_loop_policy()
    if isinstance(current_policy, selector_policy):
        return

    asyncio.set_event_loop_policy(selector_policy())


def get_worker_event_loop() -> asyncio.AbstractEventLoop:
    global _worker_event_loop

    if _worker_event_loop is None or _worker_event_loop.is_closed():
        _worker_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_event_loop)

    return _worker_event_loop
