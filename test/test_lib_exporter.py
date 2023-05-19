import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from lib.exporter import read_carrier_exporter, Exporter
from lib import carriers
import models


class mocked_carrier_exporter(carriers.Carrier):
    def get_shipment_data(self, shipment_id: str) -> models.CarrierResults:
        return models.CarrierResults(success = True, message = {"Mocked key": "Mocked value"})
    
    def create_new_shipment(self, carrier_model: models.CarrierResults) -> models.ShipmentConfirmation:
        return models.ShipmentConfirmation(status=201, result_code="Mocked result code", message="Mocked message")

class mocked_carrier_exporter_error(carriers.Carrier):
    def get_shipment_data(self, shipment_id: str) -> models.CarrierResults:
        return models.CarrierResults(success = False, message = {"Mocked error key": "Mocked error value"})
    
    def create_new_shipment(self, carrier_model: models.CarrierResults) -> models.ShipmentConfirmation:
        return models.ShipmentConfirmation(status=418, result_code="Mocked Error", message="Mocked error message")

@patch("lib.exporter.carriers.GLS")
@patch("lib.exporter.carriers.TransMission")
def test_read_carrier_exporter_none(mocked_TransMission, mocked_gls):
    result  = read_carrier_exporter('Not existing customer')
    assert result == None

@patch("lib.exporter.carriers.GLS")
@patch("lib.exporter.carriers.TransMission")
def test_read_carrier_exporter_GLS(mocked_TransMission, mocked_gls):
    result = read_carrier_exporter('GLS')
    assert result._extract_mock_name() == "GLS()"  # type: ignore

@patch("lib.exporter.carriers.GLS")
@patch("lib.exporter.carriers.TransMission")
def test_read_carrier_exporter_TransMission(mocked_TransMission, mocked_gls):
    result = read_carrier_exporter('TMS')
    assert result._extract_mock_name() == "TransMission()"  # type: ignore

@patch("lib.exporter.Jeeves")
@patch("lib.exporter.Exporter._get_exporter")
def test_Exporter_init(mocked_get_exporter: MagicMock, mocked_jeeves: MagicMock):
    mocked_get_exporter.return_value = 'Mocked exporter'
    mocked_jeeves.return_value = 'Mocked jeeves'
    exporter_object = Exporter('123456-789')
    assert exporter_object.jeeves_object == 'Mocked jeeves'
    assert exporter_object.shipment_id == '123456-789'
    assert exporter_object.carrier_exporter == 'Mocked exporter'

@patch("lib.exporter.Jeeves")
def test_Exporter_get_exporter_carrier_not_found(mocked_jeeves: MagicMock):
    jeeves_instance = MagicMock()
    jeeves_instance.check_carrier_name.return_value = models.ExporterResults(message="Mocked error message")
    mocked_jeeves.return_value = jeeves_instance
    with pytest.raises(HTTPException) as error:
        Exporter('123456-789')
    assert str(error) == "<ExceptionInfo HTTPException(status_code=404, detail={'error': True, 'error_description': 'Mocked error message'}) tblen=3>"

@patch("lib.exporter.Jeeves")
@patch("lib.exporter.read_carrier_exporter")
def test_Exporter_get_exporter_carrier_no_exporter(mocked_read_carrier_exporter: MagicMock, mocked_jeeves: MagicMock):
    jeeves_instance = MagicMock()
    jeeves_instance.check_carrier_name.return_value = models.ExporterResults(success = True, message="Not configured customer name")
    mocked_jeeves.return_value = jeeves_instance
    mocked_read_carrier_exporter.return_value = None
    with pytest.raises(HTTPException) as error:
        Exporter('123456-789')
    assert str(error) == "<ExceptionInfo HTTPException(status_code=404, detail={'error': True, 'error_description': 'Carrier with name Not configured customer name not configured in integration'}) tblen=3>"
     
@patch("lib.exporter.Jeeves")
@patch("lib.exporter.read_carrier_exporter")
def test_Exporter_get_exporter(mocked_read_carrier_exporter: MagicMock, mocked_jeeves: MagicMock):
    jeeves_instance = MagicMock()
    jeeves_instance.check_carrier_name.return_value = models.ExporterResults(success = True, message="Not configured customer name")
    mocked_jeeves.return_value = jeeves_instance
    mocked_read_carrier_exporter.return_value = "Some Exporter"
    results = Exporter('123456-789')
    assert results.carrier_exporter == "Some Exporter"
    
@patch("lib.exporter.Jeeves")
@patch("lib.exporter.Exporter._get_exporter")
def test_Exporter_get_shipment_data_error(mocked_get_exporter: MagicMock, mocked_jeeves: MagicMock):
    mocked_get_exporter.return_value = mocked_carrier_exporter_error()
    mocked_jeeves.return_value = 'Mocked jeeves'
    exporter_object = Exporter('123456-789')
    with pytest.raises(HTTPException) as error:
        exporter_object.get_shipment_data()
    assert str(error) == "<ExceptionInfo HTTPException(status_code=409, detail={'error': True, 'error_description': {'Mocked error key': 'Mocked error value'}}) tblen=2>"

@patch("lib.exporter.Jeeves")
@patch("lib.exporter.Exporter._get_exporter")
def test_Exporter_get_shipment_data(mocked_get_exporter: MagicMock, mocked_jeeves: MagicMock):
    mocked_get_exporter.return_value = mocked_carrier_exporter()
    mocked_jeeves.return_value = 'Mocked jeeves'
    exporter_object = Exporter('123456-789')
    assert exporter_object.get_shipment_data() == models.CarrierResults(success = True, message = {"Mocked key": "Mocked value"})
    
@patch("lib.exporter.Jeeves")
@patch("lib.exporter.Exporter._get_exporter")
@patch("lib.exporter.Exporter.get_shipment_data")
def test_Exporter_add_new_shipment_error(mocked_get_shipment_data, mocked_get_exporter: MagicMock, mocked_jeeves: MagicMock):
    mocked_get_shipment_data.return_value = 'Some shipment data'
    mocked_get_exporter.return_value = mocked_carrier_exporter_error()
    mocked_jeeves.return_value = 'Mocked jeeves'
    exporter_object = Exporter('123456-789')
    with pytest.raises(HTTPException) as error:
        exporter_object.add_new_shipment()
    assert str(error) == "<ExceptionInfo HTTPException(status_code=400, detail={'model': {'status': 418, 'result_code': 'Mocked Error', 'message': 'Mocked error message', 'data': None, 'meta': None}}) tblen=2>"

@patch("lib.exporter.Jeeves")
@patch("lib.exporter.Exporter._get_exporter")
@patch("lib.exporter.Exporter.get_shipment_data")
def test_Exporter_add_new_shipment(mocked_get_shipment_data, mocked_get_exporter: MagicMock, mocked_jeeves: MagicMock):
    mocked_get_shipment_data.return_value = 'Some shipment data'
    mocked_get_exporter.return_value = mocked_carrier_exporter()
    mocked_jeeves.return_value = 'Mocked jeeves'
    exporter_object = Exporter('123456-789')
    assert exporter_object.add_new_shipment() == models.ShipmentConfirmation(status=201, result_code="Mocked result code", message="Mocked message")
    

