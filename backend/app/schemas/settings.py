from pydantic import BaseModel, EmailStr, Field, TypeAdapter, field_validator

from .common import Input, Short


class SettingsUpdate(Input):
    siteName: Short | None = None
    description: str | None = Field(default=None, max_length=1000)
    contactEmail: str | None = Field(default=None, max_length=254)
    registration: str | None = Field(default=None, max_length=200)

    @field_validator('contactEmail')
    @classmethod
    def valid_email(cls, value):
        return str(TypeAdapter(EmailStr).validate_python(value)) if value else value


class PublicSettings(BaseModel):
    siteName: str
    description: str


class SettingsRead(PublicSettings):
    contactEmail: str
    registration: str
