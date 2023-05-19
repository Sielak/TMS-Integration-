from datetime import date
from pydantic import BaseModel, Field, validator
from typing import Optional, List


class srv_bool(BaseModel):
    rod: bool = False   # [rod] => bool - usługa ROD
    s10: bool = False   # [s10] => bool - usługa dostawy do 10:00
    s12: bool = False   # [s12] => bool - usługa dostawy do 12:00
    sat: bool = False   # [sat] => bool - usługa dostawy w sobotę
    ow: bool = False    # [ow] => bool - usługa "Odbiór własny"

class parcel(BaseModel):
  reference: str = Field(..., max_length=25)
  weight: float

class items(BaseModel):
  items: List[parcel] = []

class GlsShipment(BaseModel):
    rname1: str = Field(..., max_length=40)
    rname2: str = Field(None, max_length=40)
    rname3: Optional[str] = Field(..., max_length=40)
    
    rcountry: str = Field(..., max_length=3)
    rzipcode: str = Field(..., max_length=16)
    rcity: str = Field(..., max_length=30)
    rstreet: str = Field(..., max_length=50)
    
    rphone: str = Field(None, max_length=20)
    rcontact: str = Field(None, max_length=40)
    references: str = Field(None, max_length=25)
    notes: str = Field(None, max_length=80)

    srv_bool: Optional[srv_bool]
    parcels: items

    @validator('rname1', 'rname2', 'rname3', 'rcountry', 'rzipcode', 'rcity', 'rstreet', 'rphone', 'rcontact',  'references', 'notes', pre=True)
    def remove_whitespace_and_truncate(cls, value, field):
        if value is not None:
          value_stripped = value.strip()
          if field.name == 'rname1':
            return value_stripped[:40]
          elif field.name == 'rname2':
            return value_stripped[:40]
          elif field.name == 'rname3':
            return value_stripped[:40]
          elif field.name == 'rstreet':
            return value_stripped[:50]
          elif field.name == 'rphone':
            return value_stripped[:20]
          elif field.name == 'rcontact':
            return value_stripped[:40]
          elif field.name == 'references':
            return value_stripped[:25]
          elif field.name == 'notes':
            return value_stripped[:80]
          else:
            return value_stripped
        return None
