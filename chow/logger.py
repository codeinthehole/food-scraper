import click


class ConsoleLogger:
    """
    Logger that prints to the console.
    """

    def __init__(self, debug_mode: bool = False) -> None:
        self.debug_mode = debug_mode

    def debug(self, msg: str) -> None:
        """
        Log at debug level.
        """
        if self.debug_mode:
            click.secho(msg, fg="yellow", err=True)

    def info(self, msg: str) -> None:
        """
        Log at info level.
        """
        click.secho(msg, fg="blue", err=True)

    def error(self, msg: str) -> None:
        """
        Log at error level.
        """
        click.secho(msg, fg="red", err=True)
