from unittest.mock import patch
#import pytest
from lib.jeeves import Jeeves
import models


class MockedObject(object):
    pass

sql_cmd_test_Jeeves_get_dict_customer_number = """
        SELECT 
            d.q_hl_dict_definition_text1
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 4 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
            AND d.q_hl_dict_definition_text2 LIKE 'customer_number'
        """

sql_cmd_check_carrier_name = """SELECT     
            x2t.transportorsnamn
        FROM 
            olh
            JOIN x2t ON olh.foretagkod = x2t.ForetagKod AND olh.TransportorsKod = x2t.TransportorsKod
        WHERE 
            olh.ForetagKod = 1810 
            AND olh.OrderNr = 654321 
            AND olh.q_hl_rownumber = 1
            """

sql_cmd_fetch_one_order = """SELECT
            [ShipmentId]
            ,[ForetagKod]
            ,[OrderNr]
            ,[q_hl_rowNumber]
            ,[q_hl_printer_IP]
        FROM 
            q_hl_TmsIntegration
        WHERE
            ShipmentId = '123456'
            """

sql_cmd_fetch_company_id = """SELECT 
	        COALESCE(olh.ordlevplats1, olh.ftgnr, '') AS ftgnr
        FROM 
            olh
        WHERE 
            olh.OrderNr = 654321
            AND olh.q_hl_rownumber = 1
            AND olh.ForetagKod = 1810
            """

sql_cmd_fetch_company_info = """SELECT 
            fr.ftgnamn
            ,fr.ftgpostadr1 
            ,fr.landskod
            ,fr.ftgpostnr
            ,fr.ftgpostadr3
            ,fr.ftgpostadr2 
        FROM 
            fr
        WHERE 
            fr.ForetagKod = 1810
            AND fr.ftgnr = 'Mocked ftgnr'
            """

sql_cmd_fetch_delivery_info = """SELECT 
            olh.q_hl_logentcontactperson
            ,olh.q_hl_logentcontactdetails
            ,oh.q_hl_emailtt
            ,olh.q_guarantid
            ,q_hl_returnDoc
            ,olh.godsmarke2
        FROM 
            olh
            join oh on olh.ForetagKod = olh.ForetagKod AND olh.OrderNr = oh.OrderNr
        WHERE 
            olh.OrderNr = 654321
            AND olh.q_hl_rownumber = 1
            AND olh.ForetagKod = 1810
            """

sql_cmd_fetch_packages_info = """SELECT 
            orpk.kollinummer
            ,orpk.artbtotvikt 
        FROM 
            [olh]
        JOIN 
            [orpk] ON 
                [olh].[ForetagKod] = [orpk].[ForetagKod] 
                AND [olh].[OrderNr] = [orpk].[OrderNr] 
                AND [olh].[OrdBerLevDat] = [orpk].[OrdBerLevDat] 
                AND [olh].[OrdLevNr] = [orpk].[OrdLevNr] 
                AND [olh].[LagStalle] = [orpk].[LagStalle] 
                AND [olh].[OrdRestNr] = [orpk].[Olh_OrdRestNr]
        WHERE 
            olh.OrderNr = 654321
            AND olh.q_hl_rownumber = 1
            AND olh.ForetagKod = 1810
            """

sql_cmd_test_Jeeves_get_dict_inventory_stock_type = """
        SELECT 
            d.q_hl_dict_definition_text2
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 6 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
        """

sql_cmd_test_Jeeves_get_dict_order_type = """
        SELECT 
            d.q_hl_dict_definition_text1
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 3 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
            AND d.q_hl_dict_definition_text2 = 2
        """

sql_cmd_test_Jeeves_get_dict_depot_number = """
        SELECT 
            d.q_hl_dict_definition_text1
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 4 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
            AND d.q_hl_dict_definition_text2 LIKE 'depot_number'
        """

sql_cmd_test_Jeeves_get_dict_visible_parts = """
        SELECT 
            d.q_hl_dict_definition_text4, 
            isNull(d.q_hl_dict_definition_text1, '') AS q_hl_dict_definition_text1
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 1 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
            AND d.q_hl_dict_definition_text2 = 2
        """

sql_cmd_test_Jeeves_get_dict_extra_text = """
        SELECT 
            d.q_hl_dict_definition_text6
        FROM 
            q_hl_dict_definition d
        WHERE 
            d.q_hl_dict_definition_groupid = 1 
            AND d.foretagkod = 1600
            AND d.q_hl_dict_object_id = 41 
            AND d.q_hl_is_prod = '1' 
            AND d.q_hl_is_active= '1'
            AND d.q_hl_dict_definition_text2 = 2
        """

sql_cmd_test_Jeeves_get_shipment_details = """
        SELECT 
            COALESCE(olh.ordlevplats1, olh.ftgnr, '') AS ftgnr
            ,CONVERT(NVARCHAR(5), cast(q_hl_deliverytimeearliest as time)) [q_hl_deliverytimeearliest]
            ,CONVERT(NVARCHAR(5), cast(q_hl_deliverytimelatest as time)) [q_hl_deliverytimelatest]
            ,olh.ordberlevdat
            ,olh.bruttovikt
            ,olh.OrdTyp
            ,isNull(olh.q_guarantid, '0') AS q_guarantid
            ,x2t.transportorsnamn
        FROM 
            olh
            JOIN x2t ON olh.foretagkod = x2t.ForetagKod AND olh.TransportorsKod = x2t.TransportorsKod
        WHERE 
            olh.ForetagKod = 1600 
            AND olh.OrderNr = 123456 
            AND olh.q_hl_rownumber = 10
        """

def test_Jeeves_init():
    res = Jeeves()
    assert 'database_name' in res.config
    assert 'database_server' in res.config
    assert 'db_username' in res.config
    assert 'db_password' in res.config

@patch("lib.jeeves.pyodbc.connect")
def test_connect2db_success(pyodbc_object):
    pyodbc_object.return_value = 'OK'
    res = Jeeves()._connect2db()
    assert res == 'OK'

@patch("lib.jeeves.pyodbc.connect")
def test_connect2db_failure(pyodbc_object):
    pyodbc_object.side_effect = TypeError('MockingError')
    with pytest.raises(Exception) as execinfo:
        Jeeves()._connect2db()
    assert str(execinfo) == "<ExceptionInfo HTTPException(status_code=401, detail={'error': True, 'error_description': 'MockingError'}) tblen=2>"

@patch('pyodbc.connect')
def test_Jeeves_fetch_data_error(mocked_pyodbc):
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .execute.side_effect \
            = TypeError('MockingFetchError')
    jeeves_object = Jeeves()
    with pytest.raises(Exception) as execinfo:
        jeeves_object.fetch_data("Select * from xare")
    assert str(execinfo) == "<ExceptionInfo HTTPException(status_code=400, detail={'error': True, 'error_description': 'MockingFetchError'}) tblen=2>"

@patch('pyodbc.connect')
def test_Jeeves_fetch_data(mocked_pyodbc):
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .fetchone.return_value \
            = ("This is a row from DB", )
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .description = [("Column1",)]
    result = Jeeves().fetch_data("Select * from xare")
    assert result == {'Column1': 'This is a row from DB'}

@patch('pyodbc.connect')
def test_Jeeves_fetch_many_data_error(mocked_pyodbc):
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .execute.side_effect \
            = TypeError('MockingFetchManyError')
    jeeves_object = Jeeves()
    with pytest.raises(Exception) as execinfo:
        jeeves_object.fetch_many_data("Select * from xare")
    assert str(execinfo) == "<ExceptionInfo HTTPException(status_code=400, detail={'error': True, 'error_description': 'MockingFetchManyError'}) tblen=2>"

@patch('pyodbc.connect')
def test_Jeeves_fetch_many_data(mocked_pyodbc):
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .fetchall.return_value \
            = [("This is a row1 from DB", ), ("This is a row2 from DB", )]
    mocked_pyodbc.return_value \
            .cursor.return_value \
            .description = [("Column1",)]
    result = Jeeves().fetch_many_data("Select * from xare")
    assert result == [{'Column1': 'This is a row1 from DB'}, {'Column1': 'This is a row2 from DB'}]

@patch('lib.jeeves.Jeeves.fetch_one_order')
def test_Jeeves_check_carrier_name_shipment_not_found(mocked_fetch_one_order):
    mocked_fetch_one_order.return_value = None
    result = Jeeves().check_carrier_name('123456')
    mocked_fetch_one_order.assert_called_with('123456')
    assert result == models.ExporterResults(message="Error - Shipment_id = 123456 not found in Jeeves")

@patch('lib.jeeves.Jeeves.fetch_data')
@patch('lib.jeeves.Jeeves.fetch_one_order')
def test_Jeeves_check_carrier_name_order_not_found(mocked_fetch_one_order, mocked_fetch_data):
    order_info = {
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    mocked_fetch_one_order.return_value = order_info
    mocked_fetch_data.return_value = None
    result = Jeeves().check_carrier_name('123456')
    mocked_fetch_data.assert_called_with(sql_cmd_check_carrier_name)
    assert result == models.ExporterResults(message="Error - Order with id = 654321 and row = 1 not found in Jeeves company: 1810")

@patch('lib.jeeves.Jeeves.fetch_data')
@patch('lib.jeeves.Jeeves.fetch_one_order')
def test_Jeeves_check_carrier_name(mocked_fetch_one_order, mocked_fetch_data):
    order_info = {
        "ForetagKod": 1810,
        "OrderNr": 654321,
        "q_hl_rowNumber": 1
    }
    mocked_fetch_one_order.return_value = order_info
    mocked_fetch_data.return_value = {"transportorsnamn": "Mocked name"}
    result = Jeeves().check_carrier_name('123456')
    mocked_fetch_data.assert_called_with(sql_cmd_check_carrier_name)
    assert result == models.ExporterResults(success=True, message="Mocked name")

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_one_order(mocked_fetch_data):
    mocked_fetch_data.return_value = {'mocked key': 'mocked value'}
    result = Jeeves().fetch_one_order('123456')
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_one_order)
    assert result == {'mocked key': 'mocked value'}

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_company_id_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves().fetch_company_id(654321, 1, 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_company_id)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_company_id(mocked_fetch_data):
    mocked_fetch_data.return_value = {"ftgnr": "Mocked ftgnr"}
    result = Jeeves().fetch_company_id(654321, 1, 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_company_id)
    assert result == "Mocked ftgnr"

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_company_info_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves().fetch_company_info("Mocked ftgnr", 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_company_info)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_company_info(mocked_fetch_data):
    fetch_company_info = {
        "ftgnamn": "Mocked ftgnamn",
        "ftgpostadr1": "Mocked ftgpostadr1",
        "landskod": "PL",
        "ftgpostnr": "Mocked ftgpostnr",
        "ftgpostadr3": "Mocked ftgpostadr3",
        "ftgpostadr2": "Mocked ftgpostadr2"
    }
    mocked_fetch_data.return_value = fetch_company_info
    result = Jeeves().fetch_company_info("Mocked ftgnr", 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_company_info)
    assert result == models.CompanyInfo(**fetch_company_info)

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_delivery_info_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves().fetch_delivery_info(654321, 1, 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_delivery_info)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_fetch_delivery_info(mocked_fetch_data):
    fetch_delivery_info = {
        "q_hl_logentcontactperson": "Mocked contact person",
        "q_hl_logentcontactdetails": "Mocked phone",
        "q_hl_emailtt": "Mocked emailt TnT",
        "q_guarantid": 2,
        "q_hl_returnDoc": True
    }
    mocked_fetch_data.return_value = fetch_delivery_info
    result = Jeeves().fetch_delivery_info(654321, 1, 1810)
    mocked_fetch_data.assert_called_with(sql_cmd_fetch_delivery_info)
    assert result == models.DeliveryInfo(**fetch_delivery_info)

@patch('lib.jeeves.Jeeves.fetch_many_data')
def test_Jeeves_fetch_packages_info_not_found(mocked_fetch_many_data):
    mocked_fetch_many_data.return_value = []
    result = Jeeves().fetch_packages_info(654321, 1, 1810)
    mocked_fetch_many_data.assert_called_with(sql_cmd_fetch_packages_info)
    assert result == []

@patch('lib.jeeves.Jeeves.fetch_many_data')
def test_Jeeves_fetch_packages_info(mocked_fetch_many_data):
    fetch_delivery_info = [
        {
           "kollinummer": 1,
            "artbtotvikt": 1.01
        },
        {
           "kollinummer": 2,
            "artbtotvikt": 2.01
        }
    ]
    mocked_fetch_many_data.return_value = fetch_delivery_info
    result = Jeeves().fetch_packages_info(654321, 1, 1810)
    mocked_fetch_many_data.assert_called_with(sql_cmd_fetch_packages_info)
    assert result == [models.Package(kollinummer=1, artbtotvikt=1.01), models.Package(kollinummer=2, artbtotvikt=2.01)]

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_inventory_stock_type(mocked_fetch_data):
    mocked_fetch_data.return_value = {"q_hl_dict_definition_text2": 'mocked q_hl_dict_definition_text2'}
    result = Jeeves()._get_dict_inventory_stock_type(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_inventory_stock_type)
    assert result == 'mocked q_hl_dict_definition_text2'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_inventory_stock_type_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves()._get_dict_inventory_stock_type(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_inventory_stock_type)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_order_type(mocked_fetch_data):
    mocked_fetch_data.return_value = {"q_hl_dict_definition_text1": "T"}
    result = Jeeves()._get_dict_order_type(1600, 2)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_order_type)
    assert result == 'T'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_order_type_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves()._get_dict_order_type(1600, 2)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_order_type)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_depot_number(mocked_fetch_data):
    mocked_fetch_data.return_value = {'q_hl_dict_definition_text1': '9800'}
    result = Jeeves()._get_dict_depot_number(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_depot_number)
    assert result == '9800'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_depot_number_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves()._get_dict_depot_number(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_depot_number)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_customer_number(mocked_fetch_data):
    mocked_fetch_data.return_value = {'q_hl_dict_definition_text1': '1'}
    result = Jeeves()._get_dict_customer_number(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_customer_number)
    assert result == '1'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_customer_number_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves()._get_dict_customer_number(1600)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_customer_number)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_visible_parts(mocked_fetch_data):
    mocked_fetch_data.return_value = '1'
    result = Jeeves()._get_dict_visible_parts(1600, 2)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_visible_parts)
    assert result == '1'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_extra_text(mocked_fetch_data):
    mocked_fetch_data.return_value = {'q_hl_dict_definition_text6': 'some_text'}
    result = Jeeves()._get_dict_extra_text(1600, 2)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_extra_text)
    assert result == 'some_text'

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_dict_extra_text_not_found(mocked_fetch_data):
    mocked_fetch_data.return_value = None
    result = Jeeves()._get_dict_extra_text(1600, 2)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_dict_extra_text)
    assert result == None

@patch('lib.jeeves.Jeeves.fetch_data')
def test_Jeeves_get_shipment_details(mocked_fetch_data):
    mocked_fetch_data.return_value = {'some key': 'some_text'}
    order_info = {
        "ForetagKod": "1600",
        "OrderNr": "123456",
        "q_hl_rowNumber": "10"
    }
    result = Jeeves()._get_shipment_details(order_info)
    mocked_fetch_data.assert_called_with(sql_cmd_test_Jeeves_get_shipment_details)
    assert result == {'some key': 'some_text'}