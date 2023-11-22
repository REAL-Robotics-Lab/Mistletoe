from csv_logger import CsvLogger
import logging
import os


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance()


@singleton
class Logger:
    logger: CsvLogger

    def __init__(self):
        # Initialize the logs folder if it doesn't already exist
        os.makedirs("logs", mode=0o777, exist_ok=True)

        self.logger = CsvLogger(
            filename="logs/log.csv",
            delimiter=",",
            level=logging.INFO,
            add_level_names=["data"],
            add_level_nums=None,
            fmt=f"%(asctime)s,%(levelname)s,%(message)s",
            datefmt="%H:%M:%S",
            max_size=1_000_000_000, # in bytes
            max_files=4,
            header=["date", "level", "column", "value"]
        )


if __name__ == "__main__":
    Logger.logger.data(["Test", 1])