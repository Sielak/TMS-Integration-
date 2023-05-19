from typing import List, Optional
from pydantic import BaseModel

class ShipmentMeta(BaseModel):
    error_list: List = []

class ShipmentData(BaseModel):
    transport_number: str

class ShipmentConfirmation(BaseModel):    
    status: int
    result_code: str = ""
    message: str = ""
    data: Optional[ShipmentData]
    meta: Optional[ShipmentMeta]