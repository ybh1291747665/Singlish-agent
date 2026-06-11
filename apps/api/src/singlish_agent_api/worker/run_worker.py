from singlish_agent_api.worker.celery_app import celery_app


def main() -> None:
    celery_app.worker_main(["worker", "--loglevel=INFO", "--pool=solo"])


if __name__ == "__main__":
    main()
