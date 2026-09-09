"""Safe, encoding-tolerant CSV access for ZIP packages."""

import csv
import io
import logging
import zipfile
from pathlib import Path, PurePosixPath


ENCODINGS = ("utf-8-sig", "utf-8", "cp950", "big5", "latin1")


class ZipCsvReader:
    def __init__(self, path: Path, logger: logging.Logger):
        self.path = path
        self.logger = logger
        self.archive = zipfile.ZipFile(path)
        self.csv_names = tuple(
            name for name in self.archive.namelist()
            if not name.endswith("/") and PurePosixPath(name).suffix.lower() == ".csv"
            and "__MACOSX" not in PurePosixPath(name).parts
        )

    def close(self) -> None:
        self.archive.close()

    def read_rows(self, name: str) -> list[list[str]]:
        raw = self.archive.read(name)
        for encoding in ENCODINGS:
            try:
                text = raw.decode(encoding)
                return list(csv.reader(io.StringIO(text, newline="")))
            except UnicodeDecodeError:
                continue
        raise UnicodeError(f"Unable to decode {name} in {self.path}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

