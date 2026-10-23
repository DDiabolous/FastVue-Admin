from datetime import date, datetime
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Gender = Literal['unspecified', 'male', 'female', 'other']


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    gender: Gender | None = None
    birthday: date | None = None
    city: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=254)
    bio: str | None = Field(default=None, max_length=500)

    @field_validator('city', 'email', 'bio', mode='before')
    @classmethod
    def normalize_text(cls, value):
        return (value.strip() or None) if isinstance(value, str) else value

    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, value):
        return 'unspecified' if value is None or value == '' else value

    @field_validator('birthday', mode='before')
    @classmethod
    def validate_date_format(cls, value):
        if value is None or value == '':
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
            raise ValueError('生日格式须为 YYYY-MM-DD')
        return value

    @field_validator('birthday')
    @classmethod
    def birthday_not_in_future(cls, value):
        if value is not None and value > date.today():
            raise ValueError('生日不能晚于当天')
        return value


class UserProfile(BaseModel):
    id: str
    phone: str
    nickname: str
    avatar_url: str
    gender: Gender
    birthday: date | None
    city: str | None
    email: str | None
    bio: str | None
