"""CSV export for scan findings."""

import csv
import io

from app.domain.models.finding import Finding


def _csv_cell(value: object) -> str:
    text = str(value or "")
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{text}"
    return text


def export_findings_csv(findings: list[Finding]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "rule_id",
            "severity",
            "confidence",
            "title",
            "resource_type",
            "resource_name",
            "file_name",
            "line_number",
            "description",
            "remediation",
        ]
    )
    for f in findings:
        writer.writerow(
            [
                _csv_cell(f.rule_id),
                _csv_cell(f.severity.value),
                _csv_cell(f.confidence.value),
                _csv_cell(f.title),
                _csv_cell(f.resource_type or ""),
                _csv_cell(f.resource_name or ""),
                _csv_cell(f.file_name or ""),
                _csv_cell(f.line_number or ""),
                _csv_cell(f.description),
                _csv_cell(f.remediation),
            ]
        )
    return output.getvalue().encode("utf-8")
