"""Generic, encoding-tolerant CSV access for supported archives."""

import csv
import io
import logging
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from .config import SUPPORTED_ARCHIVE_SUFFIXES


ENCODINGS = ("utf-8-sig", "utf-8", "cp950", "big5", "latin1")


def archive_suffix(path: Path) -> str:
    lower = path.name.lower()
    return next((suffix for suffix in SUPPORTED_ARCHIVE_SUFFIXES if lower.endswith(suffix)), "")


def archive_stem(path: Path) -> str:
    suffix = archive_suffix(path)
    return path.name[:-len(suffix)] if suffix else path.stem


def _normalized_member(name: str) -> str:
    normalized = name.replace("\\", "/")
    original_parts = PurePosixPath(normalized).parts
    if not normalized or PurePosixPath(normalized).is_absolute() or ".." in original_parts:
        raise ValueError(f"Unsafe archive member path: {name}")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    parts = PurePosixPath(normalized).parts
    if parts and ":" in parts[0]:
        raise ValueError(f"Unsafe archive member path: {name}")
    return "/".join(parts)


class ArchiveCsvReader:
    """Expose CSV member names/rows without leaking archive-specific APIs."""

    def __init__(self, path: Path, logger: logging.Logger):
        self.path = path
        self.logger = logger
        self.kind = archive_suffix(path)
        self._archive = None
        self._members: dict[str, object] = {}
        self._sevenzip_temp: tempfile.TemporaryDirectory | None = None
        self._sevenzip_fallback = False
        if not self.kind:
            raise ValueError(f"Unsupported archive type: {path}")
        try:
            if self.kind == ".zip":
                self._open_zip()
            elif self.kind in {".tar", ".tar.gz", ".tgz"}:
                self._open_tar()
            else:
                self._open_7z()
        except Exception as exc:
            self.close()
            raise ValueError(f"Unable to read archive {path}: {exc}") from exc
        self.csv_names = tuple(sorted(self._members))

    def _accept(self, name: str) -> str | None:
        normalized = _normalized_member(name)
        parts = PurePosixPath(normalized).parts
        if PurePosixPath(normalized).suffix.lower() != ".csv" or "__MACOSX" in parts:
            return None
        return normalized

    def _open_zip(self) -> None:
        self._archive = zipfile.ZipFile(self.path)
        for info in self._archive.infolist():
            if not info.is_dir():
                accepted = self._accept(info.filename)
                if accepted:
                    self._members[accepted] = info

    def _open_tar(self) -> None:
        self._archive = tarfile.open(self.path, "r:*")
        for member in self._archive.getmembers():
            if member.isfile():
                accepted = self._accept(member.name)
                if accepted:
                    self._members[accepted] = member

    def _open_7z(self) -> None:
        try:
            import py7zr
        except ImportError:
            self._open_7z_with_bsdtar()
            return
        originals = {}
        self._sevenzip_temp = tempfile.TemporaryDirectory(prefix="aruba-fatp-7z-")
        with py7zr.SevenZipFile(self.path, mode="r") as archive:
            for name in archive.getnames():
                accepted = self._accept(name)
                if accepted:
                    originals[accepted] = name
            if originals:
                archive.extract(
                    path=self._sevenzip_temp.name,
                    targets=list(originals.values()),
                )
        for normalized, original in originals.items():
            self._members[normalized] = Path(self._sevenzip_temp.name, *PurePosixPath(_normalized_member(original)).parts)

    def _open_7z_with_bsdtar(self) -> None:
        try:
            result = subprocess.run(["tar", "-tf", str(self.path)], check=True,
                                    capture_output=True, text=True, encoding="utf-8")
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError("Reading .7z requires py7zr (or a bsdtar fallback)") from exc
        self._sevenzip_fallback = True
        for name in result.stdout.splitlines():
            accepted = self._accept(name)
            if accepted:
                self._members[accepted] = name

    def _read_bytes(self, name: str) -> bytes:
        member = self._members[name]
        if self.kind == ".zip":
            return self._archive.read(member)
        if self.kind in {".tar", ".tar.gz", ".tgz"}:
            stream = self._archive.extractfile(member)
            return stream.read() if stream else b""
        if self._sevenzip_fallback:
            return subprocess.run(["tar", "-xOf", str(self.path), str(member)], check=True,
                                  capture_output=True).stdout
        return Path(member).read_bytes()

    def read_rows(self, name: str) -> list[list[str]]:
        raw = self._read_bytes(name)
        for encoding in ENCODINGS:
            try:
                return list(csv.reader(io.StringIO(raw.decode(encoding), newline="")))
            except UnicodeDecodeError:
                continue
        raise UnicodeError(f"Unable to decode {name} in {self.path}")

    def close(self) -> None:
        if self._archive is not None:
            self._archive.close()
        if self._sevenzip_temp is not None:
            self._sevenzip_temp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

