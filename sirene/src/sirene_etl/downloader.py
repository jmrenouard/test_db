"""HTTP downloader, data.gouv.fr API resolver, and checksum verifier."""

from __future__ import annotations

import functools
import hashlib
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlsplit

import httpx

try:
    from tenacity import (
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )
except ImportError:  # pragma: no cover - lightweight fallback when tenacity is absent
    _F = TypeVar("_F", bound=Callable[..., Any])

    def stop_after_attempt(max_attempt_number: int) -> int:
        return max_attempt_number

    def wait_exponential(
        multiplier: float = 1.0,
        min: float = 0.0,
        max: float = 60.0,
    ) -> tuple[float, float, float]:
        return (multiplier, min, max)

    def retry_if_exception_type(
        exception_types: type[BaseException] | tuple[type[BaseException], ...],
    ) -> tuple[type[BaseException], ...]:
        if isinstance(exception_types, tuple):
            return exception_types
        return (exception_types,)

    def retry(
        *,
        reraise: bool = True,
        stop: int = 4,
        wait: tuple[float, float, float] = (1.0, 1.0, 10.0),
        retry: tuple[type[BaseException], ...] = (Exception,),
    ) -> Callable[[_F], _F]:
        def decorator(func: _F) -> _F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                multiplier, min_wait, max_wait = wait
                last_exc: BaseException | None = None
                for attempt in range(1, stop + 1):
                    try:
                        return func(*args, **kwargs)
                    except retry as exc:
                        last_exc = exc
                        if attempt >= stop:
                            break
                        delay = min(max_wait, max(min_wait, multiplier * (2 ** (attempt - 1))))
                        time.sleep(delay)
                if reraise and last_exc is not None:
                    raise last_exc
                return None

            return wrapper  # type: ignore[return-value]

        return decorator


CHUNK_SIZE_BYTES = 1_048_576
_SUPPORTED_HASH_ALGORITHMS = frozenset({"sha256", "sha1", "md5"})
_EXCLUDED_RESOURCE_TOKENS = (
    "historique",
    "lienssuccession",
    "doublon",
)
_FORMAT_PRIORITY = {
    "parquet": 4,
    "zip": 3,
    "csv.zip": 3,
    "csv.gz": 2,
    "gz": 2,
    "csv": 1,
}


def _normalize_hash_algorithm(algorithm: str) -> str:
    algo = (algorithm or "sha256").strip().lower().replace("-", "")
    if algo not in _SUPPORTED_HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported checksum algorithm {algorithm!r}; "
            f"expected one of {sorted(_SUPPORTED_HASH_ALGORITHMS)}."
        )
    return algo


def compute_file_checksum(file_path: Path, algorithm: str = "sha256") -> str:
    """Compute a file's cryptographic hex digest reading in 1 MiB chunks."""
    path = Path(file_path)
    algo = _normalize_hash_algorithm(algorithm)
    hasher = hashlib.new(algo)
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_SIZE_BYTES):
            hasher.update(chunk)
    return hasher.hexdigest()


def _infer_format(resource: dict[str, Any]) -> str:
    raw_fmt = str(resource.get("format") or "").strip().lower().lstrip(".")
    if raw_fmt:
        return raw_fmt
    url = str(resource.get("url") or "")
    path = urlsplit(url).path.lower()
    if path.endswith(".csv.gz"):
        return "csv.gz"
    suffix = Path(path).suffix.lstrip(".").lower()
    return suffix


def _classify_resource_entity(resource: dict[str, Any]) -> tuple[str | None, bool]:
    title = str(resource.get("title") or "")
    url = str(resource.get("url") or "")
    normalized = re.sub(r"[^a-z0-9]", "", f"{title} {url}".lower())

    if any(token in normalized for token in _EXCLUDED_RESOURCE_TOKENS):
        return (None, False)

    is_full_stock = "actif" not in normalized and "geoloc" not in normalized
    if "stockunitelegale" in normalized or (
        "unitelegale" in normalized and "stock" in normalized
    ):
        return ("UNITE_LEGALE", is_full_stock)
    if "stocketablissement" in normalized or (
        "etablissement" in normalized and "stock" in normalized
    ):
        return ("ETABLISSEMENT", is_full_stock)
    return (None, False)


def _extract_checksum_fields(
    resource: dict[str, Any],
) -> tuple[str | None, str | None]:
    checksum_obj = resource.get("checksum")
    if isinstance(checksum_obj, dict):
        ctype = checksum_obj.get("type") or resource.get("checksum_type")
        cval = checksum_obj.get("value") or resource.get("checksum_value")
    else:
        ctype = resource.get("checksum_type")
        cval = resource.get("checksum_value")

    norm_type = str(ctype).strip().lower() if ctype else None
    norm_val = str(cval).strip().lower() if cval else None
    return (norm_type or None, norm_val or None)


def extract_sirene_resources_from_payload(
    payload: dict[str, Any],
    preferred_format: str = "parquet",
) -> dict[str, dict[str, Any]]:
    """Select current StockUniteLegale and StockEtablissement entries from dataset JSON."""
    pref_fmt = (preferred_format or "parquet").strip().lower().lstrip(".")
    resources = payload.get("resources") or []
    best: dict[str, tuple[tuple[Any, ...], dict[str, Any]]] = {}

    for res in resources:
        if not isinstance(res, dict):
            continue
        entity_type, is_full_stock = _classify_resource_entity(res)
        if entity_type is None:
            continue
        url = str(res.get("url") or "").strip()
        if not url:
            continue

        fmt = _infer_format(res)
        checksum_type, checksum_value = _extract_checksum_fields(res)
        last_modified = res.get("last_modified") or res.get("updated_at")
        score = (
            1 if fmt == pref_fmt else 0,
            1 if is_full_stock else 0,
            _FORMAT_PRIORITY.get(fmt, 0),
            1 if checksum_value else 0,
            str(last_modified or ""),
        )
        entry = {
            "resource_id": str(res.get("id") or res.get("resource_id") or ""),
            "title": str(res.get("title") or ""),
            "url": url,
            "format": fmt,
            "last_modified": last_modified,
            "checksum_type": checksum_type,
            "checksum_value": checksum_value,
            "filesize": res.get("filesize"),
        }
        current = best.get(entity_type)
        if current is None or score > current[0]:
            best[entity_type] = (score, entry)

    return {entity: data for entity, (_, data) in best.items()}


def fetch_datagouv_sirene_resources(
    api_url: str,
    preferred_format: str = "parquet",
    timeout: float = 30.0,
) -> dict[str, dict[str, Any]]:
    """Fetch dataset metadata from data.gouv.fr and resolve current Sirene stock files."""

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    def _get_json() -> dict[str, Any]:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(api_url)
            response.raise_for_status()
            return dict(response.json())

    payload = _get_json()
    return extract_sirene_resources_from_payload(
        payload,
        preferred_format=preferred_format,
    )


def download_with_verification(
    url: str,
    dest_path: Path,
    expected_checksum: str | None = None,
    checksum_type: str = "sha256",
    timeout: float = 60.0,
) -> tuple[Path, str]:
    """Stream a file to a .part staging file, verify checksum, and atomically rename."""
    target = Path(dest_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    part_path = target.with_suffix(target.suffix + ".part")
    algo = _normalize_hash_algorithm(checksum_type)

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    def _stream_once() -> str:
        hasher = hashlib.new(algo)
        try:
            with httpx.stream(
                "GET",
                url,
                timeout=timeout,
                follow_redirects=True,
            ) as response:
                response.raise_for_status()
                with part_path.open("wb") as handle:
                    for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE_BYTES):
                        if chunk:
                            handle.write(chunk)
                            hasher.update(chunk)
        except Exception:
            part_path.unlink(missing_ok=True)
            raise
        return hasher.hexdigest()

    actual_checksum = _stream_once()
    if expected_checksum is not None and expected_checksum.strip():
        expected_norm = expected_checksum.strip().lower()
        if actual_checksum.lower() != expected_norm:
            part_path.unlink(missing_ok=True)
            raise ValueError(
                f"checksum mismatch for {url}: expected {expected_norm} ({algo}), "
                f"got {actual_checksum}."
            )

    part_path.replace(target)
    return (target, actual_checksum)
