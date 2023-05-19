from pydantic import BaseModel
from typing import Dict


class CarrierResults(BaseModel):
    """Model for storing data that will be sent to carrier

    Keys:
        success (bool): Indicates if extraction was done successfully
        message (Dict): Dictionary with carrier model or with error description
    """    
    success: bool = False
    message: Dict = {}