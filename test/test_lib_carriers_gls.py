import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi import HTTPException
import socket
from lib.carriers.gls import GLS
import models
from zeep.exceptions import Fault, ValidationError


@pytest.fixture
def mocked_zeep_Client(mocker):
    return mocker.patch('zeep.Client')

@pytest.fixture
def mocked_zeep_Transport():
    with patch("lib.carriers.gls.Transport") as mocked_zeep_Transport:
        mocked_zeep_Transport.return_value = "Some Transport"
        yield mocked_zeep_Transport

@pytest.fixture
def mocked_auth_to_gls():
    with patch("lib.carriers.gls.GLS._auth_to_gls") as mocked_auth_to_gls:
        mocked_auth_to_gls.return_value = "Some Token"
        yield mocked_auth_to_gls

def test_GLS_init(mocked_zeep_Client: MagicMock, mocked_zeep_Transport, mocked_auth_to_gls):
    gls_object = GLS()
    mocked_zeep_Client.assert_called_with(wsdl='https://ade-test.gls-poland.com/adeplus/pm1/ade_webapi2.php?wsdl', transport='Some Transport')
    assert gls_object.token == "Some Token"

def test_GLS_auth_to_gls(mocked_zeep_Client: MagicMock, mocked_zeep_Transport):
    GLS()
    assert mocked_zeep_Client().service.__getitem__.call_args_list[0][0][0] == 'adeLogin'

@patch("lib.carriers.gls.zeep.Client.service")
@patch("lib.carriers.gls.GLS._get_shipment_label")
@patch("lib.carriers.gls.GLS._print_shipment_label")
@patch("lib.carriers.gls.GLS._get_track_and_trace_number")
def test_GLS_create_new_shipment(
        mocked_get_track_and_trace_number: MagicMock, 
        mocked_print_shipment_label: MagicMock,
        mocked_get_shipment_label: MagicMock,
        mocked_zeep_service: MagicMock, mocked_auth_to_gls):   
    mocked_get_track_and_trace_number.return_value = 'shipment_id'
    errors = models.ShipmentMeta(error_list=['MockedError'])
    mocked_print_shipment_label.return_value = errors
    mocked_get_shipment_label.return_value = 'Mocked label'
    service = Mock(return_value="Some value")
    mocked_zeep_service.__getitem__ = Mock(return_value=service)
    gls_object = GLS()
    result = gls_object.create_new_shipment(models.CarrierResults(message={"mocked key": "Mocked message"}))
    assert result == models.ShipmentConfirmation(status=201, message="shipment_id", meta=errors)

@patch("lib.carriers.gls.zeep.Client.service")
def test_GLS_create_new_shipment_error(mocked_zeep_service: MagicMock, mocked_auth_to_gls):    
    service = Mock(side_effect=Fault(message='Mocked message', code="Mocked code", actor="Mocked actor"))
    mocked_zeep_service.__getitem__ = Mock(return_value=service)
    gls_object = GLS()
    with pytest.raises(HTTPException) as error:
        gls_object.create_new_shipment(models.CarrierResults(message={"mocked key": "Mocked message"}))
    assert str(error) == "<ExceptionInfo HTTPException(status_code=409, detail={'message': 'Mocked message', 'code': 'Mocked code', 'endpoint': 'Mocked actor'}) tblen=2>"

@patch("lib.carriers.gls.zeep.Client.service")
def test_GLS_create_new_shipment_validation_error(mocked_zeep_service: MagicMock, mocked_auth_to_gls):    
    service = Mock(side_effect=ValidationError())
    mocked_zeep_service.__getitem__ = Mock(return_value=service)
    gls_object = GLS()
    with pytest.raises(HTTPException) as error:
        gls_object.create_new_shipment(models.CarrierResults(message={"mocked key": "Mocked message"}))
    assert str(error) == "<ExceptionInfo HTTPException(status_code=409, detail={'message': 'No parcels found for this shipment!'}) tblen=2>"

@patch("lib.carriers.gls.zeep.Client.service")
def test_GLS_get_track_and_trace_number(mocked_zeep_service: MagicMock, mocked_auth_to_gls):    
    service = Mock(return_value={"parcels": {"items": [{"number": "123456"}, {"number": "654321"}]}})
    mocked_zeep_service.__getitem__ = Mock(return_value=service)
    gls_object = GLS()
    assert gls_object._get_track_and_trace_number(shipment_id=123456) == "123456,654321"

@patch("lib.carriers.gls.socket")
def test_GLS_print_shipment_label(mocked_socket: MagicMock, mocked_auth_to_gls):    
    mocked_socket.return_value = 'Some mock'
    gls_object = GLS()
    result = gls_object._print_shipment_label(label_content="U29tZUxhYmVs", printer_ip="SomeIP")
    assert result == models.ShipmentMeta()

def test_GLS_print_shipment_label_printer_ip_none(mocked_auth_to_gls):    
    gls_object = GLS()
    result = gls_object._print_shipment_label(label_content="U29tZUxhYmVs", printer_ip=None)
    assert result == models.ShipmentMeta(error_list=["Printer IP not provided"])

def test_GLS_print_shipment_label_printer_ip_empty(mocked_auth_to_gls):    
    gls_object = GLS()
    result = gls_object._print_shipment_label(label_content="U29tZUxhYmVs", printer_ip='')
    assert result == models.ShipmentMeta(error_list=["Printer IP not provided"])

@patch("lib.carriers.gls.socket.socket.connect")
def test_GLS_print_shipment_label_error(mocked_socket: MagicMock, mocked_auth_to_gls): 
    mocked_socket.side_effect = socket.error
    gls_object = GLS()
    result = gls_object._print_shipment_label(label_content="U29tZUxhYmVs", printer_ip="SomeIP")
    assert result == models.ShipmentMeta(error_list=["Error with the connection"])

@patch("lib.carriers.gls.zeep.Client.service")
def test_GLS_get_shipment_label(mocked_zeep_service: MagicMock, mocked_auth_to_gls):    
    service = Mock(return_value="Some value")
    mocked_zeep_service.__getitem__ = Mock(return_value=service)
    gls_object = GLS()
    assert gls_object._get_shipment_label(shipment_id=123456) == "Some value"

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_order_not_found(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    jeeves_instance.fetch_one_order.return_value = None
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    assert result == models.CarrierResults(message={"error_details": "Order with shipment id 123456-789 not found in Jeeves"})

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_company_id_not_found(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = None
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    assert result == models.CarrierResults(message={"error_details": "Cant find company id for order 654321 in jeeves"})

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_company_info_not_found(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = None
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    assert result == models.CarrierResults(message={"error_details": "Cant fetch company info for customer 00001 from jeeves"})

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_delivery_info_not_found(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "Mocked landskod",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = fetch_company_info
    jeeves_instance.fetch_delivery_info.return_value = None
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    assert result == models.CarrierResults(message={"error_details": "Cant fetch delivery info for order 654321 from jeeves"})

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_q_guarantid_1(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "PL",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = models.CompanyInfo(**fetch_company_info)
    jeeves_instance.fetch_delivery_info.return_value = models.DeliveryInfo(
        q_hl_logentcontactperson="Mocked contact person",
        q_hl_logentcontactdetails="Mocked phone",
        q_hl_emailtt="Mocked emailt TnT",
        q_guarantid=1,
        q_hl_returnDoc=True
    )
    jeeves_instance.fetch_packages_info.return_value = [models.Package(kollinummer=1, artbtotvikt=1.01)]
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    expected_message = {
        'rname1': 'Mocked ftgnamn', 
        'rname2': 'Mocked ftgpostadr1', 
        'rname3': 'Mocked contact person', 
        'rcountry': 'PL', 
        'rzipcode': 'Mocked ftgpostnr', 
        'rcity': 'Mocked ftgpostadr3', 
        'rstreet': 'Mocked ftgpostadr2', 
        'rphone': 'Mocked phone', 
        'rcontact': 'Mocked emailt TnT', 
        'references': '654321_1', 
        'notes': None,
        'srv_bool': {
            'rod': True, 
            's10': True, 
            's12': False, 
            'sat': False, 
            'ow': False
        }, 
        'parcels': {
            'items': [
                {
                    'reference': '654321_1', 
                    'weight': 1.01
                }
            ]
        }
    }
    assert result.message == expected_message
    assert result == models.CarrierResults(success=True, message=expected_message)

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_q_guarantid_2(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "PL",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = models.CompanyInfo(**fetch_company_info)
    jeeves_instance.fetch_delivery_info.return_value = models.DeliveryInfo(
        q_hl_logentcontactperson="Mocked contact person",
        q_hl_logentcontactdetails="Mocked phone",
        q_hl_emailtt="Mocked emailt TnT",
        q_guarantid=2,
        q_hl_returnDoc=False,
        godsmarke2='Some_very_long_text_that_have_more_then_80_characters_to_achive_that_I_need_to_write_another_sentence_here'
    )
    jeeves_instance.fetch_packages_info.return_value = [models.Package(kollinummer=1, artbtotvikt=1.01)]
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    expected_message = {
        'rname1': 'Mocked ftgnamn', 
        'rname2': 'Mocked ftgpostadr1', 
        'rname3': 'Mocked contact person', 
        'rcountry': 'PL', 
        'rzipcode': 'Mocked ftgpostnr', 
        'rcity': 'Mocked ftgpostadr3', 
        'rstreet': 'Mocked ftgpostadr2', 
        'rphone': 'Mocked phone', 
        'rcontact': 'Mocked emailt TnT', 
        'references': '654321_1', 
        'notes': "Some_very_long_text_that_have_more_then_80_characters_to_achive_that_I_need_to_w",
        'srv_bool': {
            'rod': False, 
            's10': False, 
            's12': True, 
            'sat': False, 
            'ow': False
        }, 
        'parcels': {
            'items': [
                {
                    'reference': '654321_1', 
                    'weight': 1.01
                }
            ]
        }
    }
    assert result == models.CarrierResults(success=True, message=expected_message)

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_q_guarantid_3(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "PL",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = models.CompanyInfo(**fetch_company_info)
    jeeves_instance.fetch_delivery_info.return_value = models.DeliveryInfo(
        q_hl_logentcontactperson="Mocked contact person",
        q_hl_logentcontactdetails="Mocked phone",
        q_hl_emailtt="Mocked emailt TnT",
        q_guarantid=3,
        q_hl_returnDoc=True
    )
    jeeves_instance.fetch_packages_info.return_value = [models.Package(kollinummer=1, artbtotvikt=1.01)]
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    expected_message = {
        'rname1': 'Mocked ftgnamn', 
        'rname2': 'Mocked ftgpostadr1', 
        'rname3': 'Mocked contact person', 
        'rcountry': 'PL', 
        'rzipcode': 'Mocked ftgpostnr', 
        'rcity': 'Mocked ftgpostadr3', 
        'rstreet': 'Mocked ftgpostadr2', 
        'rphone': 'Mocked phone', 
        'rcontact': 'Mocked emailt TnT', 
        'references': '654321_1', 
        'notes': None,
        'srv_bool': {
            'rod': True, 
            's10': False, 
            's12': False, 
            'sat': True, 
            'ow': False
        }, 
        'parcels': {
            'items': [
                {
                    'reference': '654321_1', 
                    'weight': 1.01
                }
            ]
        }
    }
    assert result == models.CarrierResults(success=True, message=expected_message)

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_q_guarantid_4(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn               ",
        "ftgpostadr1": "Mocked ftgpostadr1          ",
        "landskod": "PL",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = models.CompanyInfo(**fetch_company_info)
    jeeves_instance.fetch_delivery_info.return_value = models.DeliveryInfo(
        q_hl_logentcontactperson="Mocked contact person",
        q_hl_logentcontactdetails="Mocked phone",
        q_hl_emailtt="Mocked emailt TnT",
        q_guarantid=4,
        q_hl_returnDoc=False
    )
    jeeves_instance.fetch_packages_info.return_value = [models.Package(kollinummer=1, artbtotvikt=1.01)]
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    expected_message = {
        'rname1': 'Mocked ftgnamn', 
        'rname2': 'Mocked ftgpostadr1', 
        'rname3': 'Mocked contact person', 
        'rcountry': 'PL', 
        'rzipcode': 'Mocked ftgpostnr', 
        'rcity': 'Mocked ftgpostadr3', 
        'rstreet': 'Mocked ftgpostadr2', 
        'rphone': 'Mocked phone', 
        'rcontact': 'Mocked emailt TnT', 
        'references': '654321_1', 
        'notes': None,
        'srv_bool': {
            'rod': False, 
            's10': False, 
            's12': False, 
            'sat': False, 
            'ow': True
        }, 
        'parcels': {
            'items': [
                {
                    'reference': '654321_1', 
                    'weight': 1.01
                }
            ]
        }
    }
    assert result == models.CarrierResults(success=True, message=expected_message)

@patch("lib.carriers.gls.Jeeves")
def test_GLS_get_shipment_data_model_error(mocked_jeeves: MagicMock, mocked_zeep_Client, mocked_zeep_Transport, mocked_auth_to_gls):    
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "123456-789",
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "PL123",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance.fetch_company_id.return_value = "00001"
    jeeves_instance.fetch_company_info.return_value = models.CompanyInfo(**fetch_company_info)
    jeeves_instance.fetch_delivery_info.return_value = models.DeliveryInfo(
        q_hl_logentcontactperson="Mocked contact person",
        q_hl_logentcontactdetails="Mocked phone",
        q_hl_emailtt="Mocked emailt TnT",
        q_guarantid=1,
        q_hl_returnDoc=True
    )
    jeeves_instance.fetch_packages_info.return_value = [models.Package(kollinummer=1, artbtotvikt=1.01)]
    mocked_jeeves.return_value = jeeves_instance
    gls_object = GLS()
    result = gls_object.get_shipment_data(shipment_id="123456-789")
    expected_message = {
        'error_details': [
            {
                'ctx': {
                    'limit_value': 3
                },
                'loc': ('rcountry',),
                'msg': 'ensure this value has at most 3 characters',
                'type': 'value_error.any_str.max_length'
            }
        ]
    }
    assert result.message == expected_message
    assert result == models.CarrierResults(success=False, message=expected_message)