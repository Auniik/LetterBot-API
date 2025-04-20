from enum import Enum

from pydantic import BaseModel, Field

class PromptType(str, Enum):
    image = "image"
    text = "text"

class PromptCategory(str, Enum):
    lifestyle = "lifestyle"
    telco = "telco"


class PromptTemplateDTO(BaseModel):
    type: PromptType = Field(
        default=None,
        description="Type of the prompt template",
        examples=["text", "image"],
    )
    template: str = Field(
        default=None,
        description="Template of the prompt",
        examples=["Hello, {name}!"],
    )
    is_default: bool = Field(
        default=None,
        description="Indicates if the prompt template is default",
        examples=[True],
    )
    category: PromptCategory = Field(
        default=None,
        description="Category of the prompt template",
        examples=["lifestyle", "telco"],
    )