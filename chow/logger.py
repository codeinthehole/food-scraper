import click


class ConsoleLogger:
    def __init__(self, debug_mode: bool = False) -> None:
        self.debug_mode = debug_mode

    def debug(self, msg: str) -> None:
        if self.debug_mode:
            click.secho(msg, fg="yellow", err=True)

    def info(self, msg: str) -> None:
        click.secho(msg, fg="blue", err=True)

    def error(self, msg: str) -> None:
        click.secho(msg, fg="red", err=True)
