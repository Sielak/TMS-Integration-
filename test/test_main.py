from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
import models


client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "<title>Transportation management system API - Swagger UI</title>" in response.text

@patch("main.Exporter")
def test_get_order_data(mocked_exporter: MagicMock):
    exporter_object = MagicMock()
    exporter_object.get_shipment_data.return_value = models.CarrierResults(success = True, message = {"msg": "This is mocked order data"})
    mocked_exporter.return_value = exporter_object
    response = client.get("/get_order_data?shipment_id=1")
    assert response.json() == {'message': {'msg': 'This is mocked order data'}, 'success': True}

@patch("main.Exporter")
def test_addShipment(mocked_exporter: MagicMock):
    exporter_object = MagicMock()
    exporter_object.add_new_shipment.return_value = models.ShipmentConfirmation(status = 201, result_code = "OK", message = "This is mocked order data")
    mocked_exporter.return_value = exporter_object
    response = client.post("/addShipment?shipment_id=1")
    expected_response = {'data': None,
          'message': 'This is mocked order data',
          'meta': None,
          'result_code': 'OK',
          'status': 201}
    assert response.json() == expected_response
