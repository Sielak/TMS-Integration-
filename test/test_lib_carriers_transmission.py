import datetime
from unittest.mock import patch, Mock, MagicMock
import pytest
from lib.carriers.transmission import TransMission
import models


@pytest.fixture
def mock_token():
    with patch('lib.carriers.transmission.TransMission._get_token') as mock_token:
        mock_token.return_value = "Some token"
        yield mock_token


@pytest.fixture
def mock_config():
    with patch('lib.carriers.transmission.json.load') as mock_config:
        mock_config.return_value = {
            "carriers": { 
                "transmission": {
                    "root_url": "mocked_url", 
                    "user": "mocked_user", 
                    "password": "mocked_pass"
                }
            }
        }
        yield mock_config


def _mock_response(
        status=200,
        content="CONTENT",
        json_data=None,
        raise_for_status=None,
        url=None,
        text=None):
    """
    since we typically test a bunch of different
    requests calls for a service, we are going to do
    a lot of mock responses, so its usually a good idea
    to have a helper function that builds these things
    """
    mock_resp = Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status  # pragma: no cover
    # set status code and content
    mock_resp.status_code = status
    mock_resp.url = url
    mock_resp.text = text
    mock_resp.content = content
    # add json data if provided
    if json_data:
        mock_resp.json = Mock(
            return_value=json_data
        )
    return mock_resp


def expected_result(
                error=True,
                row_data=True,
                shipment_data=None,
                inventory_stock_type='',
                order_type=None,
                depot_number=None,
                error_type='',
                service_code='',
                LoadingMeter='',
                Measures='',
                Volume='',
                customer_number=''
            ):
    if error_type == 'order_not_found':
        error_desc = 'Order with that id not found in Jeeves'
    elif error_type == 'stock_type':
        error_desc = 'Missing configuration - Inventory Stock type'
    elif error_type == 'olh.OrdTyp':
        error_desc = 'olh.OrdTyp is empty'
    elif error_type == 'order_type':
        error_desc = 'Missing configuration - Order type'
    elif error_type == 'depot_number':
        error_desc = 'Missing configuration - Depot Number'
    elif error_type == 'visible_parts':
        error_desc = 'Missing configuration - Visible parts'
    elif error_type == 'emballagetyp':
        error_desc = 'orpk.emballagetyp IS NULL'
    elif error_type == 'dictPackageType':
        error_desc = 'Missing configuration - Package type'
    elif error_type == 'unitMeasure':
        error_desc = 'Missing configuration - Unit measure'
    else:
        error_desc = ''
    if row_data is True:
        row_data = {'ForetagKod': 1810,
                     'OrderNr': 123,
                     'ShipmentId': 'T_001',
                     'q_hl_rowNumber': 10}
    else:
        row_data = None
    if customer_number != '':
        customer_number = int(customer_number)
    data2return = {
        'LoadingMeter': LoadingMeter,
        'Measures': Measures,
        'Volume': Volume,
        'customer_number': customer_number,
        'depot_number': depot_number,
        'error': error,
        'error_description': error_desc,
        'extra_text': '',
        'inventory_stock_type': inventory_stock_type,
        'order_type': order_type,
        'row_data': row_data,
        'service_code': service_code,
        'shipment_data': shipment_data
    }
    return data2return

@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_init(mocked_jeeves, mock_token, mock_config):
    mocked_jeeves.return_value = "Mock for jeeves"
    transmisstion_object = TransMission()
    assert transmisstion_object.token == "Some token"
    assert transmisstion_object.jeeves_object == "Mock for jeeves"
    assert transmisstion_object.config == {'root_url': 'mocked_url', 'user': 'mocked_user', 'password': 'mocked_pass'}
    assert isinstance(transmisstion_object.shipment_data, models.TransmissionShipment)

@patch("lib.carriers.transmission.requests.post")
def test_TransMission_get_token(requests_object, mock_config):
    mock_resp = _mock_response(content="token_check", json_data={
                               "access_token": "123456"})
    requests_object.return_value = mock_resp
    transmisstion_object = TransMission()
    assert transmisstion_object.token == "123456"

@patch("lib.carriers.transmission.requests.post")
def test_TransMission_get_token_error(requests_object, mock_config):
    mock_resp = _mock_response(content="token_check", json_data={
                               "not_access_token": "123456"})
    requests_object.return_value = mock_resp
    with pytest.raises(Exception) as e_info:
        TransMission()
    assert str(
        e_info.value) == "Problem with getting token > {'not_access_token': '123456'}"

@patch("lib.carriers.transmission.requests.post")
def test_TransMission_create_new_shipment(requests_object, mock_token, mock_config):
    mock_resp = _mock_response(json_data={"status": 201, "message": "Mocked response"})
    requests_object.return_value = mock_resp
    data2send = models.CarrierResults(success=True, message={"status": 201, "message": "Test message"})
    carrier_object = TransMission()
    result = carrier_object.create_new_shipment(data2send)
    requests_object.assert_called_with('mocked_url/shipments/shipment', data='{"status": 201, "message": "Test message"}', headers={'Authorization': 'Bearer Some token', 'Content-Type': 'application/json'})
    assert result == models.ShipmentConfirmation(status=201, message="Mocked response")

@patch("lib.carriers.transmission.TransMission._get_data")
def test_TransMission_get_shipment_data_error(mocked_get_data, mock_token, mock_config):
    mocked_get_data.return_value = (None, models.TransmissionShipment(error=True, error_description="Mocked error"))
    carrier_object = TransMission()
    result = carrier_object.get_shipment_data("123456")
    assert result == models.CarrierResults(message={"error_details": "Mocked error"})

@patch("lib.carriers.transmission.TransMission._get_data")
def test_TransMission_get_shipment_data(mocked_get_data, mock_token, mock_config):
    model = {
        'type': 'T', 
        'depot_number': '0001', 
        'customer_number': 9999, 
        'date': None, 
        'created_by': None, 
        'references': [
            {
                'type': 'Some type', 
                'reference': 'Some reference'
            }
        ], 
        'addresses': [
            {
                'type': 'mock_type', 
                'name': 'mock_name', 
                'name2': None, 
                'address1': 'mock_address1', 
                'housenumber': '1', 
                'postalcode': '123456', 
                'city': 'mock_city', 
                'country_code': 'PL', 
                'contact': None, 
                'date': None, 
                'timeframes': None
            }
        ], 
        'text_messages': None, 
        'Shipment_services': None, 
        'shipment_units': [
            {
                'unit_number': 1, 
                'barcode': None, 
                'description': None, 
                'contains_packages': None, 
                'unit_type': 'EP', 
                'measurements': {
                    'weight': 1.12, 
                    'length': None, 
                    'width': None, 
                    'height': None, 
                    'loadingmeter': None, 
                    'volume': None
                }, 
                'references': [], 
                'dangerous_goods': None
            }
        ], 
        'labels': None}
    mocked_get_data.return_value = (model, models.TransmissionShipment())
    carrier_object = TransMission()
    result = carrier_object.get_shipment_data("123456")
    assert result == models.CarrierResults(success=True, message=models.shipment(**model))

@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
def test_TransMission_get_data_order_not_found_error(fetch_order):
    fetch_order.return_value = None
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(error_type='order_not_found', row_data=False, inventory_stock_type='')

@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
@patch("lib.carriers.transmission.Jeeves._get_dict_inventory_stock_type")
def test_TransMission_get_data_stock_type_error(stock_type, fetch_order):
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    stock_type.return_value = None
    fetch_order.return_value = fetch_order_data
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(error_type='stock_type')


@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
@patch("lib.carriers.transmission.Jeeves._get_dict_inventory_stock_type")
@patch("lib.carriers.transmission.Jeeves._get_shipment_details")
def test_TransMission_get_data_ordTyp_error(shipment_details, stock_type, fetch_order):
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1
    }
    shipment_data = {
        'OrdTyp': None,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    fetch_order.return_value = fetch_order_data
    stock_type.return_value = "stock_01"
    shipment_details.return_value = shipment_details_data
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(shipment_data=shipment_data,
                                            error_type='olh.OrdTyp', inventory_stock_type='stock_01')


@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
@patch("lib.carriers.transmission.Jeeves._get_dict_inventory_stock_type")
@patch("lib.carriers.transmission.Jeeves._get_shipment_details")
@patch("lib.carriers.transmission.Jeeves._get_dict_order_type")
def test_TransMission_get_data_order_type_error(dict_order_type, shipment_details, stock_type, fetch_order):
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    fetch_order.return_value = fetch_order_data
    stock_type.return_value = "stock_01"
    shipment_details.return_value = shipment_details_data
    dict_order_type.return_value = None
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(shipment_data=shipment_data,
                                            error_type='order_type', inventory_stock_type='stock_01')


@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
@patch("lib.carriers.transmission.Jeeves._get_dict_inventory_stock_type")
@patch("lib.carriers.transmission.Jeeves._get_shipment_details")
@patch("lib.carriers.transmission.Jeeves._get_dict_order_type")
@patch("lib.carriers.transmission.Jeeves._get_dict_depot_number")
def test_TransMission_get_data_depot_number_error(dict_depot_number, dict_order_type, shipment_details, stock_type, fetch_order):
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    fetch_order.return_value = fetch_order_data
    stock_type.return_value = "stock_01"
    shipment_details.return_value = shipment_details_data
    dict_order_type.return_value = 'mocked order type'
    dict_depot_number.return_value = None
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(shipment_data=shipment_data, error_type='depot_number',
                                            inventory_stock_type='stock_01', order_type='mocked order type')


@patch("lib.carriers.transmission.Jeeves.fetch_one_order")
@patch("lib.carriers.transmission.Jeeves._get_dict_inventory_stock_type")
@patch("lib.carriers.transmission.Jeeves._get_shipment_details")
@patch("lib.carriers.transmission.Jeeves._get_dict_order_type")
@patch("lib.carriers.transmission.Jeeves._get_dict_depot_number")
@patch("lib.carriers.transmission.Jeeves._get_dict_customer_number")
@patch("lib.carriers.transmission.Jeeves._get_dict_visible_parts")
def test_TransMission_get_data_visible_parts_error(dict_visible_parts, dict_customer_number, dict_depot_number, dict_order_type, shipment_details, stock_type, fetch_order):
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    fetch_order.return_value = fetch_order_data
    stock_type.return_value = "stock_01"
    shipment_details.return_value = shipment_details_data
    dict_order_type.return_value = 'mocked order type'
    dict_depot_number.return_value = "mocked depot number"
    dict_customer_number.return_value = ""
    dict_visible_parts.return_value = None
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(
        shipment_data=shipment_data,
        error_type='visible_parts',
        inventory_stock_type='stock_01',
        order_type='mocked order type',
        depot_number="mocked depot number"
    )

@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_get_data_emballagetyp_error(mocked_jeeves, mock_token, mock_config):
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance._get_dict_inventory_stock_type.return_value = "stock_01"
    jeeves_instance._get_shipment_details.return_value = shipment_details_data
    jeeves_instance._get_dict_order_type.return_value = 'mocked order type'
    jeeves_instance._get_dict_depot_number.return_value = "mocked depot number"
    jeeves_instance._get_dict_customer_number.return_value = ""
    jeeves_instance._get_dict_visible_parts.return_value = {
        "q_hl_dict_definition_text4": "measures, loading meter, volume",
        "q_hl_dict_definition_text1": ""
    }
    jeeves_instance._get_dict_extra_text.return_value = '' 
    jeeves_instance.fetch_data.side_effect = [
        'mock adrContact',
        'mock adrDelivery',
        'mock textMsg',
        None,
        'mock dictPackageType',
        'mock unitMeasure'
    ]
    jeeves_instance.fetch_many_data.return_value = [{'KolliNummer': 'mock curShipUnit_KolliNummer', 'packages': 'mock curShipUnit_packages'}]
    mocked_jeeves.return_value = jeeves_instance
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(
        error_type='emballagetyp', 
        inventory_stock_type='stock_01',
        depot_number="mocked depot number",
        Volume='1',
        Measures='1',
        LoadingMeter='1',
        order_type="mocked order type", 
        shipment_data=shipment_data)


@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_get_data_dictPackageType_error(mocked_jeeves, mock_token, mock_config):
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance._get_dict_inventory_stock_type.return_value = "stock_01"
    jeeves_instance._get_shipment_details.return_value = shipment_details_data
    jeeves_instance._get_dict_order_type.return_value = 'mocked order type'
    jeeves_instance._get_dict_depot_number.return_value = "mocked depot number"
    jeeves_instance._get_dict_customer_number.return_value = ""
    jeeves_instance._get_dict_visible_parts.return_value = {
        "q_hl_dict_definition_text4": "measures, loading meter, volume",
        "q_hl_dict_definition_text1": ""
    }
    jeeves_instance._get_dict_extra_text.return_value = '' 
    jeeves_instance.fetch_data.side_effect = [
        'mock adrContact',
        'mock adrDelivery',
        'mock textMsg',
        {'emballagetyp': 'mock emballage_typ'},
        None,
        'mock unitMeasure'
    ]
    jeeves_instance.fetch_many_data.return_value = [{'KolliNummer': 'mock curShipUnit_KolliNummer', 'packages': 'mock curShipUnit_packages'}]
    mocked_jeeves.return_value = jeeves_instance
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(
        error_type='dictPackageType', 
        inventory_stock_type='stock_01',
        depot_number="mocked depot number",
        Volume='1',
        Measures='1',
        LoadingMeter='1',
        order_type="mocked order type", 
        shipment_data=shipment_data)

@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_get_data_unitMeasure_error(mocked_jeeves, mock_token, mock_config):
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date(2021, 12, 20),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance._get_dict_inventory_stock_type.return_value = "stock_01"
    jeeves_instance._get_shipment_details.return_value = shipment_details_data
    jeeves_instance._get_dict_order_type.return_value = 'mocked order type'
    jeeves_instance._get_dict_depot_number.return_value = "mocked depot number"
    jeeves_instance._get_dict_customer_number.return_value = ""
    jeeves_instance._get_dict_visible_parts.return_value = {
        "q_hl_dict_definition_text4": "measures, loading meter, volume",
        "q_hl_dict_definition_text1": ""
    }
    jeeves_instance._get_dict_extra_text.return_value = '' 
    jeeves_instance.fetch_data.side_effect = [
        'mock adrContact',
        'mock adrDelivery',
        'mock textMsg',
        {'emballagetyp': 'mock emballage_typ'},
        {'q_hl_dict_definition_text1': 'mock emballage_typ'},
        None
    ]
    jeeves_instance.fetch_many_data.return_value = [{'KolliNummer': 'mock curShipUnit_KolliNummer', 'packages': 'mock curShipUnit_packages'}]
    mocked_jeeves.return_value = jeeves_instance
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    assert result.dict() == expected_result(
        error_type='unitMeasure', 
        inventory_stock_type='stock_01',
        depot_number="mocked depot number",
        Volume='1',
        Measures='1',
        LoadingMeter='1',
        order_type="mocked order type", 
        shipment_data=shipment_data)

@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_get_data(mocked_jeeves, mock_token, mock_config):
    jeeves_instance = MagicMock()
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": "2021-12-20",
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': datetime.date.today(),
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance._get_dict_inventory_stock_type.return_value = "stock_01"
    jeeves_instance._get_shipment_details.return_value = shipment_details_data
    jeeves_instance._get_dict_order_type.return_value = 'T'
    jeeves_instance._get_dict_depot_number.return_value = "1234"
    jeeves_instance._get_dict_customer_number.return_value = 123456
    jeeves_instance._get_dict_visible_parts.return_value = {
        "q_hl_dict_definition_text4": "measures, loading meter, volume",
        "q_hl_dict_definition_text1": "m"
    }
    jeeves_instance._get_dict_extra_text.return_value = '' 
    jeeves_instance.fetch_data.side_effect = [
        {'email_address': None, 'language': None, 'name': None, 'phonenumber': None},
        {'type': '1', 'name': '2', 'address1': '3', 'housenumber': '4', 'postalcode': '5', 'city': '6', 'country_code': '7'},
        {'type': 'AFLINFO', 'remarks': 'mocked remarks'},
        {'emballagetyp': 'm'},
        {'q_hl_dict_definition_text1': 'm'},
        {
            'height': None,
            'length': None,
            'loadingmeter': None,
            'volume': None,
            'weight': '1.2',
            'width': None
        }
    ]
    jeeves_instance.fetch_many_data.return_value = [{'KolliNummer': 'mock curShipUnit_KolliNummer', 'packages': 1}]
    mocked_jeeves.return_value = jeeves_instance
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    expected_model = {
        'Shipment_services': [{'service_code': 'm'}],
        'addresses': [{'address1': '3',
                    'city': '6',
                    'contact': {'email_address': None,
                                'language': None,
                                'name': None,
                                'phonenumber': None},
                    'country_code': '7',
                    'housenumber': '4',
                    'name': '2',
                    'postalcode': '5',
                    'timeframes': [{'time_from': None,
                                    'time_to': None}],
                    'type': '1'}],
        'created_by': '',
        'customer_number': 123456,
        'date': datetime.date.today(),
        'depot_number': '1234',
        'labels': '',
        'references': [{'reference': '123_10',
                        'type': 'NRORDER'}],
        'shipment_units': [{'barcode': '',
                            'contains_packages': 1,
                            'description': '',
                            'measurements': {'height': None,
                                            'length': None,
                                            'loadingmeter': None,
                                            'volume': None,
                                            'weight': 1.2,
                                            'width': None},
                            'references': [{'reference': 123,
                                            'type': 'delivery_note'}],
                            'unit_number': 1,
                            'unit_type': 'm'}],
        'text_messages': [{'remarks': 'mocked remarks',
                        'type': 'AFLINFO'}],
        'type': 'T'
    }
    assert model == expected_model
    assert result.dict() == expected_result(
        error=False,
        inventory_stock_type='stock_01',
        customer_number="123456",
        depot_number="1234",
        Volume='1',
        Measures='1',
        LoadingMeter='1',
        order_type="T", 
        service_code='m',
        shipment_data=shipment_data)

@patch("lib.carriers.transmission.Jeeves")
def test_TransMission_get_data_future_date(mocked_jeeves, mock_token, mock_config):
    jeeves_instance = MagicMock()
    future_date = datetime.date.today() + datetime.timedelta(days = 3) 
    fetch_order_data = {
        "ShipmentId": "T_001",
        "ForetagKod": 1810,
        "OrderNr": 123,
        "q_hl_rowNumber": 10
    }
    shipment_details_data = {
        "ftgnr": "123456",
        "ordberlevdat": future_date,
        "bruttovikt": 1.1,
        "q_guarantid": 1,
        "OrdTyp": 1
    }
    shipment_data = {
        'OrdTyp': 1,
        'bruttovikt': 1.1,
        'ftgnr': '123456',
        'ordberlevdat': future_date,
        'q_guarantid': 1,
        'q_hl_deliverytimeearliest': None,
        'q_hl_deliverytimelatest': None
    }
    jeeves_instance.fetch_one_order.return_value = fetch_order_data
    jeeves_instance._get_dict_inventory_stock_type.return_value = "stock_01"
    jeeves_instance._get_shipment_details.return_value = shipment_details_data
    jeeves_instance._get_dict_order_type.return_value = 'T'
    jeeves_instance._get_dict_depot_number.return_value = "1234"
    jeeves_instance._get_dict_customer_number.return_value = 123456
    jeeves_instance._get_dict_visible_parts.return_value = {
        "q_hl_dict_definition_text4": "measures, loading meter, volume",
        "q_hl_dict_definition_text1": "m"
    }
    jeeves_instance._get_dict_extra_text.return_value = '' 
    jeeves_instance.fetch_data.side_effect = [
        {'email_address': None, 'language': None, 'name': None, 'phonenumber': None},
        {'type': '1', 'name': '2', 'address1': '3', 'housenumber': '4', 'postalcode': '5', 'city': '6', 'country_code': '7'},
        {'type': 'AFLINFO', 'remarks': 'mocked remarks'},
        {'emballagetyp': 'm'},
        {'q_hl_dict_definition_text1': 'm'},
        {
            'height': None,
            'length': None,
            'loadingmeter': None,
            'volume': None,
            'weight': '1.2',
            'width': None
        }
    ]
    jeeves_instance.fetch_many_data.return_value = [{'KolliNummer': 'mock curShipUnit_KolliNummer', 'packages': 1}]
    mocked_jeeves.return_value = jeeves_instance
    carrier_object = TransMission()
    model, result = carrier_object._get_data('123456-678')
    expected_model = {
        'Shipment_services': [{'service_code': 'm'}],
        'addresses': [{'address1': '3',
                    'city': '6',
                    'contact': {'email_address': None,
                                'language': None,
                                'name': None,
                                'phonenumber': None},
                    'country_code': '7',
                    'housenumber': '4',
                    'name': '2',
                    'postalcode': '5',
                    'timeframes': [{'time_from': None,
                                    'time_to': None}],
                    'type': '1'}],
        'created_by': '',
        'customer_number': 123456,
        'date': future_date,
        'depot_number': '1234',
        'labels': '',
        'references': [{'reference': '123_10',
                        'type': 'NRORDER'}],
        'shipment_units': [{'barcode': '',
                            'contains_packages': 1,
                            'description': '',
                            'measurements': {'height': None,
                                            'length': None,
                                            'loadingmeter': None,
                                            'volume': None,
                                            'weight': 1.2,
                                            'width': None},
                            'references': [{'reference': 123,
                                            'type': 'delivery_note'}],
                            'unit_number': 1,
                            'unit_type': 'm'}],
        'text_messages': [{'remarks': 'mocked remarks',
                        'type': 'AFLINFO'}],
        'type': 'T'
    }
    assert model == expected_model
    assert result.dict() == expected_result(
        error=False,
        inventory_stock_type='stock_01',
        customer_number="123456",
        depot_number="1234",
        Volume='1',
        Measures='1',
        LoadingMeter='1',
        order_type="T", 
        service_code='m',
        shipment_data=shipment_data)