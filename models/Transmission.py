from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


class references(BaseModel):
    type: str = Field(..., max_length=18)
    reference: str = Field(..., max_length=30)

class contact(BaseModel):
    name: str = Field(None, max_length=60)
    phonenumber: str = Field(None, max_length=15)
    email_address: str = Field(None, max_length=180)
    language: str = Field(None, max_length=2)

class timeframes(BaseModel):
    time_from: str = Field(None, max_length=5)
    time_to: str = Field(None, max_length=5)

class addresses(BaseModel):
    type: str = Field(..., max_length=16)
    name: str = Field(..., max_length=60)
    name2: str = Field(None, max_length=60)
    address1: str = Field(..., max_length=60)
    housenumber: str = Field(..., max_length=10)
    postalcode: str = Field(..., max_length=10)
    city: str = Field(..., max_length=60)
    country_code: str = Field(..., max_length=2)
    contact: Optional[contact]
    date: Optional[date] 
    timeframes: Optional[List[timeframes]]

class text_messages(BaseModel):
    type: str = Field(..., max_length=16)
    remarks: str = Field(..., max_length=180)

class Shipment_services(BaseModel):
    service_code: str = Field(..., max_length=10)

class measurements(BaseModel):
    weight: float
    length: int = Field(None, le=99999)
    width: int = Field(None, le=99999)
    height: int = Field(None, le=99999)
    loadingmeter: Optional[float]
    volume: Optional[float]

class dangerous_goods(BaseModel):
    un_number: int = Field(..., le=9999)
    un_name: str = Field(..., max_length=180)
    un_class: int = Field(..., le=99999)
    un_sub_class: str = Field(..., max_length=10)
    quantity: int = Field(..., le=9999999999)
    weight: float
    chemical_description: str = Field(..., max_length=180)
    packing_group: str = Field(..., max_length=5)
    packing_description: str = Field(..., max_length=180)
    danger_label_main: str = Field(..., max_length=5)
    danger_label_add_1: str = Field(..., max_length=5)
    danger_label_add_2: str = Field(..., max_length=5)
    danger_label_add_3: str = Field(..., max_length=5)
    transport_category: str = Field(..., max_length=5)
    tunnel_code: str = Field(..., max_length=5)
    environmentally_hazardous: bool
    multiplier: int = Field(..., le=999)

class shipment_units(BaseModel):
    unit_number: int = Field(..., le=999)
    barcode: str = Field(None, max_length=60) 
    description: str = Field(None, max_length=120) 
    contains_packages:  int = Field(None, le=9999999999)
    unit_type: str = 'EP'
    measurements:  measurements
    references:  List[references]
    dangerous_goods: Optional[List[dangerous_goods]]

class shipment(BaseModel):    
    type: str = Field(..., max_length=1)
    depot_number: str = Field(..., max_length=4)  # should be INT but then transmission API dont work
    customer_number: int = Field(..., le=999999)
    date: Optional[date]
    created_by: str = Field(None, max_length=30)
    references: List[references]
    addresses: List[addresses]
    text_messages: Optional[List[text_messages]]
    Shipment_services: Optional[List[Shipment_services]]
    shipment_units: List[shipment_units]
    labels: Optional[str]
