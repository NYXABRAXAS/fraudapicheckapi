from datetime import datetime, timezone


def test_fraud_check_returns_decision(client, auth_headers) -> None:
    payload = {
        "customer_id": "LOS-1001",
        "name": "Amit Kumar",
        "pan": "ABCDE1234F",
        "mobile": "9876543210",
        "email": "amit@mailinator.com",
        "ip_address": "192.168.1.20",
        "income": 3000000,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_fingerprint": "device-1",
    }
    response = client.post("/fraud-check", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "fraud_score" in data
    assert data["decision"] in {"APPROVE", "REVIEW", "REJECT"}
