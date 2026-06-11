from singlish_agent_api.worker import runtime


def test_configure_worker_event_loop_uses_selector_policy_on_windows(monkeypatch) -> None:
    configured: list[str] = []

    class FakeSelectorPolicy:
        pass

    class FakeOtherPolicy:
        pass

    monkeypatch.setattr(runtime.sys, "platform", "win32")
    monkeypatch.setattr(runtime.asyncio, "WindowsSelectorEventLoopPolicy", FakeSelectorPolicy)
    monkeypatch.setattr(runtime.asyncio, "get_event_loop_policy", lambda: FakeOtherPolicy())
    monkeypatch.setattr(
        runtime.asyncio,
        "set_event_loop_policy",
        lambda policy: configured.append(type(policy).__name__),
    )

    runtime.configure_worker_event_loop()

    assert configured == ["FakeSelectorPolicy"]


def test_configure_worker_event_loop_skips_non_windows(monkeypatch) -> None:
    called: list[bool] = []

    monkeypatch.setattr(runtime.sys, "platform", "linux")
    monkeypatch.setattr(
        runtime.asyncio,
        "set_event_loop_policy",
        lambda policy: called.append(True),
    )

    runtime.configure_worker_event_loop()

    assert called == []
