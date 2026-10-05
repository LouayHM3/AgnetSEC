from app import app


def test_health_endpoint_reports_demo_mode():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok', 'mode': 'demo', 'service': 'agentsec'}


def test_scan_request_requires_target():
    client = app.test_client()
    response = client.post('/api/scans', json={'ports': '80'})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'A valid target is required'
