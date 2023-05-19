from pydantic import BaseModel, Field
from typing import Optional, List


class ExporterResults(BaseModel):
    success: bool = False
    message: str = 'Error'

class OrderData(BaseModel):
    ShipmentId: str
    ForetagKod: int
    OrderNr: int
    q_hl_rowNumber: int
    q_hl_printer_IP: Optional[str] = ""

class CompanyInfo(BaseModel):
    ftgnamn: Optional[str]
    ftgpostadr1: Optional[str]
    landskod: Optional[str]
    ftgpostnr: Optional[str]
    ftgpostadr3: Optional[str]
    ftgpostadr2 : Optional[str]

class DeliveryInfo(BaseModel):
    q_hl_logentcontactperson: Optional[str]
    q_hl_logentcontactdetails: Optional[str]
    q_hl_emailtt: Optional[str]
    q_guarantid: Optional[int]
    q_hl_returnDoc: Optional[bool] = False
    godsmarke2: Optional[str]

class Package(BaseModel):
    kollinummer: int
    artbtotvikt: float
