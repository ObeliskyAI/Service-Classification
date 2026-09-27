from pydantic import BaseModel, Field, ConfigDict


class ClassificationRequest(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "EMERGENCY": "NO",
                "Provider Name": "ABC Radiology Center",
                "SERVICE DESC": "MRI"
            }
        }
    )

    EMERGENCY: str

    provider_name: str = Field(
        alias="Provider Name"
    )

    service_description: str = Field(
        alias="SERVICE DESC"
    )




class BenfitsRequest(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "DRC CODE": "DRC001: Exception - Teeth not covered under this plan"
            }
        }
    )

    drc_code: str = Field(
        alias="DRC CODE"
    )
