import logging


class Logger:

    def __init__(self, name: str, level: int):

        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.log_handler: logging.Handler = logging.StreamHandler()
        self.log_handler.setLevel(level)

        self.log_formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
        )

        self.log_handler.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_handler)

    def log(self, level: int, message: str):
        self.logger.log(level, message)
