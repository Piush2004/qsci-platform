import pytest

from qsci_core.confidence.decomposition import compute_confidence
from qsci_core.financial.eoq import CostAssumptions, total_inventory_cost
from qsci_core.persistence import db
from qsci_core.persistence.models import AuditRecord, RecommendationRecord
from qsci_core.recommendation.builder import build_recommendation
from qsci_core.risk.stockout_risk import stockout_risk_from_quantiles


def _sample_recommendation(sku_id="TEST_SKU"):
    risk = stockout_risk_from_quantiles(p10=38, p50=45, p90=55, reorder_point=40)
    conf = compute_confidence(0.9, 0.7, 0.85, 0.8)
    fin = total_inventory_cost(
        avg_inventory_units=100, orders_per_year=12, expected_stockout_units=2,
        costs=CostAssumptions(2.0, 50.0, 10.0),
    )
    return build_recommendation(sku_id, 38, 45, 55, suggested_order_qty=200, reorder_point=40, risk=risk, confidence=conf, financial_impact=fin)


def test_build_recommendation_rejects_out_of_order_quantiles():
    risk = stockout_risk_from_quantiles(p10=38, p50=45, p90=55, reorder_point=40)
    conf = compute_confidence(0.9, 0.7, 0.85, 0.8)
    with pytest.raises(ValueError):
        build_recommendation("X", forecast_p10=60, forecast_p50=45, forecast_p90=55, suggested_order_qty=1, reorder_point=1, risk=risk, confidence=conf, financial_impact={})


def test_build_recommendation_rejects_negative_order_qty():
    risk = stockout_risk_from_quantiles(p10=38, p50=45, p90=55, reorder_point=40)
    conf = compute_confidence(0.9, 0.7, 0.85, 0.8)
    with pytest.raises(ValueError):
        build_recommendation("X", 38, 45, 55, suggested_order_qty=-1, reorder_point=1, risk=risk, confidence=conf, financial_impact={})


def test_recommendation_risk_level_bucketing():
    # A reorder point far below the demand distribution (p10=40) leaves an
    # inadequate buffer -> HIGH stockout risk. One far above (p90=60) leaves
    # ample buffer -> LOW risk. See test_risk.py for the underlying model.
    inadequate_buffer = stockout_risk_from_quantiles(p10=40, p50=50, p90=60, reorder_point=10)
    ample_buffer = stockout_risk_from_quantiles(p10=40, p50=50, p90=60, reorder_point=100)
    conf = compute_confidence(0.9, 0.7, 0.85, 0.8)
    fin = {"status": "ILLUSTRATIVE"}
    rec_high_risk = build_recommendation("X", 40, 50, 60, 10, 10, inadequate_buffer, conf, fin)
    rec_low_risk = build_recommendation("X", 40, 50, 60, 10, 100, ample_buffer, conf, fin)
    assert rec_high_risk.risk_level == "HIGH"
    assert rec_low_risk.risk_level == "LOW"


@pytest.fixture
def session(tmp_path):
    engine = db.get_engine(tmp_path / "test.db")
    s = db.get_session(engine)
    yield s
    s.close()
    engine.dispose()


def test_persist_recommendation_creates_audit_event(session):
    rec = _sample_recommendation()
    row = db.persist_recommendation(session, rec)
    assert row.id is not None
    events = session.query(AuditRecord).filter_by(recommendation_id=row.id).all()
    assert [e.event_type for e in events] == ["RECOMMENDATION_CREATED"]


def test_record_approval_modify_requires_qty(session):
    rec = _sample_recommendation()
    row = db.persist_recommendation(session, rec)
    from qsci_core.persistence.models import ApprovalDecision
    with pytest.raises(ValueError):
        db.record_approval(session, row.id, ApprovalDecision.MODIFY, approver="jane")


def test_record_approval_approve_rejects_modified_qty(session):
    rec = _sample_recommendation()
    row = db.persist_recommendation(session, rec)
    from qsci_core.persistence.models import ApprovalDecision
    with pytest.raises(ValueError):
        db.record_approval(session, row.id, ApprovalDecision.APPROVE, approver="jane", modified_qty=5.0)


def test_record_approval_unknown_recommendation_raises(session):
    from qsci_core.persistence.models import ApprovalDecision
    with pytest.raises(ValueError):
        db.record_approval(session, 9999, ApprovalDecision.APPROVE, approver="jane")


def test_full_chain_recommendation_approval_outcome_audit_order(session):
    from qsci_core.persistence.models import ApprovalDecision
    rec = _sample_recommendation()
    row = db.persist_recommendation(session, rec)
    db.record_approval(session, row.id, ApprovalDecision.MODIFY, approver="jane", modified_qty=150.0)
    db.record_outcome(session, row.id, actual_qty_ordered=150.0, actual_demand_observed=47.0)

    events = session.query(AuditRecord).filter_by(recommendation_id=row.id).order_by(AuditRecord.id).all()
    assert [e.event_type for e in events] == ["RECOMMENDATION_CREATED", "APPROVAL_MODIFY", "OUTCOME_RECORDED"]

    stored = session.get(RecommendationRecord, row.id)
    assert len(stored.approvals) == 1
    assert len(stored.outcomes) == 1
    assert stored.approvals[0].modified_qty == 150.0
