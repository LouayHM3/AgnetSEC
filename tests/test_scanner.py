from scanner import calculate_score, risk_level


def test_score_uses_report_penalties():
    findings = [{"severity": "critical"}, {"severity": "medium"}, {"severity": "low"}]
    assert calculate_score(findings) == 44


def test_false_positive_does_not_reduce_score():
    assert calculate_score([{"severity": "critical", "false_positive": True}]) == 100


def test_risk_boundaries():
    assert risk_level(40) == "CRITICAL"
    assert risk_level(65) == "HIGH"
    assert risk_level(85) == "MEDIUM"
    assert risk_level(86) == "LOW"
