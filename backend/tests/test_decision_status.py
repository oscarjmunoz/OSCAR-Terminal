from app.core.DecisionStatus import DecisionStatus


def test_decision_status_enum_values() -> None:
    assert DecisionStatus.PASS.value == "PASS"
    assert DecisionStatus.FAIL.value == "FAIL"
    assert DecisionStatus.WAIT.value == "WAIT"
    assert DecisionStatus.WARNING.value == "WARNING"
    assert DecisionStatus.READY.value == "READY"


def test_decision_status_has_expected_members() -> None:
    expected = {"PASS", "FAIL", "WAIT", "WARNING", "READY"}
    assert {status.name for status in DecisionStatus} == expected