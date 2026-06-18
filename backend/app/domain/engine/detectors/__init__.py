"""Detector registry."""

from collections.abc import Callable

from app.domain.engine.detectors import (
    db_public,
    hardcoded_secrets,
    iam_wildcard,
    missing_backups,
    missing_encryption,
    missing_logging,
    s3_public,
    sg_overly_permissive,
    sg_rdp_open,
    sg_ssh_open,
)
from app.domain.engine.models import Detection, ScanContext

DetectorFunc = Callable[[ScanContext], list[Detection]]

ALL_DETECTORS: list[tuple[str, DetectorFunc]] = [
    (s3_public.RULE_ID, s3_public.detect),
    (sg_ssh_open.RULE_ID, sg_ssh_open.detect),
    (sg_rdp_open.RULE_ID, sg_rdp_open.detect),
    (iam_wildcard.RULE_ID, iam_wildcard.detect),
    (missing_encryption.RULE_ID, missing_encryption.detect),
    (db_public.RULE_ID, db_public.detect),
    (missing_logging.RULE_ID, missing_logging.detect),
    (missing_backups.RULE_ID, missing_backups.detect),
    (hardcoded_secrets.RULE_ID, hardcoded_secrets.detect),
    (sg_overly_permissive.RULE_ID, sg_overly_permissive.detect),
]
