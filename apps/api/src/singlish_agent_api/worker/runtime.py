import asyncio
import sys


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
