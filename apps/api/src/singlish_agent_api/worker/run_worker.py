from singlish_agent_api.worker.celery_app import celery_app
from singlish_agent_api.worker.runtime import configure_worker_event_loop


def main() -> None:
    configure_worker_event_loop()
    celery_app.worker_main(["worker", "--loglevel=INFO", "--pool=solo"])


if __name__ == "__main__":
    main()
