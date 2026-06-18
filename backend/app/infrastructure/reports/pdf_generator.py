"""Professional PDF report generator for security scans."""

from __future__ import annotations

import io
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.domain.models.finding import Finding
from app.domain.models.scan import Scan
from app.domain.services.scoring import compute_grade
from app.infrastructure.reports.recommendations import build_recommendations

MAX_FINDINGS_IN_REPORT = 200


def _esc(text: str | None) -> str:
    return escape(text or "")


def _section_heading(text: str, styles) -> Paragraph:
    return Paragraph(text, styles["SectionHeading"])


def _format_dt(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%Y-%m-%d %H:%M UTC")


def generate_scan_pdf(
    scan: Scan,
    findings: list[Finding],
    generated_at: datetime | None = None,
) -> bytes:
    """Generate a PDF report with summary, findings, risk score, and recommendations."""
    generated_at = generated_at or datetime.now(timezone.utc).replace(tzinfo=None)
    recommendations = build_recommendations(findings)
    grade = compute_grade(scan.risk_score)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"Security Scan Report - {scan.label or scan.id[:8]}",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#0f172a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#475569"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="FindingTitle",
            parent=styles["Normal"],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=2,
            textColor=colors.HexColor("#0f172a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="FindingBody",
            parent=styles["Normal"],
            fontSize=9,
            leftIndent=12,
            textColor=colors.HexColor("#334155"),
        )
    )

    story: list = []
    title = scan.label or f"Scan {scan.id[:8]}"
    story.append(Paragraph(f"Security Scan Report", styles["Title"]))
    story.append(Paragraph(_esc(title), styles["Heading3"]))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"<b>Generated:</b> {generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Meta"],
        )
    )
    story.append(Spacer(1, 16))

    # Scan summary
    story.append(_section_heading("1. Scan Summary", styles))
    summary_rows = [
        ["Scan ID", _esc(scan.id)],
        ["Label", _esc(title)],
        ["Status", _esc(scan.status.value.replace("_", " ").title())],
        ["Created", _format_dt(scan.created_at)],
        ["Completed", _format_dt(scan.completed_at)],
        ["Files Scanned", str(scan.file_count)],
        ["Resources Parsed", str(scan.resource_count)],
        ["Duration", f"{scan.duration_ms / 1000:.1f}s" if scan.duration_ms else "—"],
        ["Parser Version", _esc(scan.parser_version or "—")],
        ["Total Findings", str(len(findings))],
        ["Critical", str(scan.critical_count)],
        ["High", str(scan.high_count)],
        ["Medium", str(scan.medium_count)],
        ["Low", str(scan.low_count)],
        ["Info", str(scan.info_count)],
    ]
    if scan.error_message:
        summary_rows.append(["Errors", _esc(scan.error_message[:200])])

    summary_table = Table(summary_rows, colWidths=[1.6 * inch, 4.6 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Risk score
    story.append(_section_heading("2. Risk Score", styles))
    score_display = scan.risk_score if scan.risk_score is not None else "—"
    risk_rows = [
        ["Security Score (0–100)", str(score_display)],
        ["Overall Grade", grade or "—"],
        ["Penalty Points", str(scan.raw_risk_score or 0)],
        ["Normalized Score", str(scan.normalized_score if scan.normalized_score is not None else "—")],
    ]
    risk_table = Table(risk_rows, colWidths=[2.0 * inch, 4.2 * inch])
    risk_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(risk_table)
    story.append(Spacer(1, 12))

    # Findings
    story.append(_section_heading("3. Findings", styles))
    if not findings:
        story.append(Paragraph("No security findings were detected.", styles["Normal"]))
    else:
        displayed = findings[:MAX_FINDINGS_IN_REPORT]
        if len(findings) > MAX_FINDINGS_IN_REPORT:
            story.append(
                Paragraph(
                    f"Showing first {MAX_FINDINGS_IN_REPORT} of {len(findings)} findings.",
                    styles["Meta"],
                )
            )
            story.append(Spacer(1, 6))

        findings_data = [["#", "Severity", "Rule", "Title", "Resource", "Location"]]
        for index, finding in enumerate(displayed, start=1):
            location = finding.file_name or "—"
            if finding.line_number is not None:
                location = f"{location} L{finding.line_number}"
            resource = finding.resource_name or finding.resource_type or "—"
            findings_data.append(
                [
                    str(index),
                    finding.severity.value.title(),
                    finding.rule_id,
                    finding.title[:48],
                    str(resource)[:28],
                    location[:32],
                ]
            )

        findings_table = Table(
            findings_data,
            colWidths=[0.35 * inch, 0.7 * inch, 0.95 * inch, 1.8 * inch, 1.2 * inch, 1.2 * inch],
            repeatRows=1,
        )
        findings_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(findings_table)
        story.append(Spacer(1, 10))

        for index, finding in enumerate(displayed, start=1):
            story.append(
                Paragraph(
                    f"<b>{index}. [{finding.severity.value.upper()}] {finding.rule_id}</b> — "
                    f"{_esc(finding.title)}",
                    styles["FindingTitle"],
                )
            )
            story.append(Paragraph(_esc(finding.description), styles["FindingBody"]))
            if finding.remediation:
                story.append(
                    Paragraph(f"<i>Remediation:</i> {_esc(finding.remediation)}", styles["FindingBody"])
                )

    story.append(Spacer(1, 12))

    # Recommendations
    story.append(_section_heading("4. Recommendations", styles))
    for index, recommendation in enumerate(recommendations, start=1):
        story.append(
            Paragraph(
                f"<b>{index}. [{recommendation['severity'].upper()}] "
                f"{_esc(recommendation['rule_id'])}</b> — {_esc(recommendation['title'])}",
                styles["FindingTitle"],
            )
        )
        story.append(Paragraph(_esc(recommendation["remediation"]), styles["FindingBody"]))

    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            f"Report generated on {generated_at.strftime('%Y-%m-%d %H:%M UTC')} by "
            "Enterprise Security Guardrail Auditor.",
            styles["Meta"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
