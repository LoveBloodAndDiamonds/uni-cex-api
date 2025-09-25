from unicex.types import LoggerLike


class Test:
    def __init__(self, logger: LoggerLike) -> None:
        self.logger = logger


def main() -> None:
    """Main entry point for the application."""

    from loguru import logger

    t = Test(logger=logger)


if __name__ == "__main__":
    main()
