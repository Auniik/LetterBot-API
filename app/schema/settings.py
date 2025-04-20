from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class SettingUpdateDTO(BaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Must be one of: string, int, bool, json",
        examples=["string", "int", "bool", "json"],
    )
    value: Optional[Union[str, int, bool, dict]] = Field(
        default=None,
        description="Value must match the selected type"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Boolean to activate or deactivate this setting"
    )

    @field_validator('type')
    def validate_type(cls, v):
        allowed = {"string", "int", "bool", "json"}
        if v and v not in allowed:
            raise ValueError(f"`type` must be one of: {', '.join(allowed)}")
        return v

    @field_validator('value')
    def validate_value(cls, v, info: ValidationInfo):
        if v is None:
            return v

        type_value = info.data.get('type')  # ✅ the new way to access sibling fields

        if type_value == 'int' and not isinstance(v, int):
            raise ValueError("`value` must be an integer when `type` is 'int'")
        elif type_value == 'bool' and not isinstance(v, bool):
            raise ValueError("`value` must be a boolean when `type` is 'bool'")
        elif type_value == 'json' and not isinstance(v, (dict, list)):
            raise ValueError("`value` must be a JSON object or array when `type` is 'json'")

        return v

