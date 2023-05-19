from typing import Optional
from pydantic import BaseModel
from datetime import date

class TransmissionRowData(BaseModel):
    ShipmentId: str
    ForetagKod: int
    OrderNr: int
    q_hl_rowNumber: int

class TransmissionShipmentData(BaseModel):
    ftgnr: str
    q_hl_deliverytimeearliest: Optional[str]
    q_hl_deliverytimelatest: Optional[str]
    ordberlevdat: date
    bruttovikt: float
    OrdTyp: Optional[int]
    q_guarantid: int

class TransmissionShipment(BaseModel):
    row_data: Optional[TransmissionRowData]
    inventory_stock_type: str = ''
    shipment_data: Optional[TransmissionShipmentData]
    order_type: Optional[str]
    depot_number: Optional[str]
    customer_number: str = ''
    service_code: str = ''
    Measures: str = ''
    Volume: str = ''
    LoadingMeter: str = ''
    extra_text: str = ''
    error: bool = False
    error_description: str = ''