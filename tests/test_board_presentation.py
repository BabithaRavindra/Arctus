import pytest
import io
from pptx import Presentation
from core.models import FinancialStatement
from core.synthetic import generate_clean_midmarket_statement
from core.cockpit import calculate_cockpit_metrics, get_default_capital_structure_for_statement
from core.board_pack import (
    THEMES,
    generate_structured_slide_narratives,
    run_presentation_qa_preflight,
    build_editable_pptx_deck,
    build_executive_pdf_deck,
)


def test_theme_definitions():
    assert "executive_gold" in THEMES
    assert "corporate_slate" in THEMES
    assert "investor_minimal" in THEMES
    assert "lender_consortium" in THEMES

    th = THEMES["executive_gold"]
    assert th.bg_color_hex == "#101722"
    assert th.accent_hex == "#B49A5A"
    assert len(th.bg_rgb) == 3


def test_qa_preflight_check():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    metrics = calculate_cockpit_metrics(stmt, cap_struct)

    res = run_presentation_qa_preflight(stmt, metrics)
    assert res.passed is True
    assert len(res.errors) == 0
    assert res.checks_performed >= 5


def test_structured_slide_narratives():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    metrics = calculate_cockpit_metrics(stmt, cap_struct)

    narratives = generate_structured_slide_narratives(stmt, metrics, audience="board")
    assert "exec_summary" in narratives
    assert "financial_performance" in narratives
    assert "debt_covenants" in narratives

    n = narratives["exec_summary"]
    assert len(n.what_happened) > 10
    assert len(n.why_it_happened) > 10
    assert len(n.financial_impact) > 10
    assert len(n.management_action) > 10
    assert len(n.traceable_source) > 10


def test_build_editable_pptx_deck():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    metrics = calculate_cockpit_metrics(stmt, cap_struct)
    narratives = generate_structured_slide_narratives(stmt, metrics, audience="board")
    theme = THEMES["executive_gold"]

    pptx_io = build_editable_pptx_deck(
        stmt=stmt,
        metrics=metrics,
        narratives=narratives,
        theme=theme,
        company_name="Apex Precision Automotives Ltd."
    )

    assert isinstance(pptx_io, io.BytesIO)
    pptx_bytes = pptx_io.getvalue()
    assert len(pptx_bytes) > 1000

    # Load back with pptx to verify it's a valid presentation
    prs = Presentation(io.BytesIO(pptx_bytes))
    assert len(prs.slides) == 5  # 5 slides created


def test_build_executive_pdf_deck():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    metrics = calculate_cockpit_metrics(stmt, cap_struct)
    narratives = generate_structured_slide_narratives(stmt, metrics, audience="board")
    theme = THEMES["executive_gold"]

    pdf_io = build_executive_pdf_deck(
        stmt=stmt,
        metrics=metrics,
        narratives=narratives,
        theme=theme,
        company_name="Apex Precision Automotives Ltd."
    )

    assert isinstance(pdf_io, io.BytesIO)
    pdf_bytes = pdf_io.getvalue()
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")  # Valid PDF magic header
