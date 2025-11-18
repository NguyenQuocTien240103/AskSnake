from pydantic import BaseModel, Field, EmailStr, root_validator
from typing import Optional, Annotated

class UserBase(BaseModel):
    email: EmailStr

class UserLogin(UserBase):
    password: Annotated[str, Field(min_length=6)]

class UserRegister(UserBase):
    password: Annotated[str, Field(min_length=6)]
    confirm_password: Annotated[str, Field(min_length=6)]
    @root_validator(pre=False, skip_on_failure=True)
    def check_passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password != confirm_password:
            raise ValueError('Passwords do not match')
        return values
class UserUpdatePassword(BaseModel):
    old_password: Annotated[str, Field(min_length=6)]
    new_password: Annotated[str, Field(min_length=6)]
    confirm_new_password: Annotated[str, Field(min_length=6)]
    @root_validator(pre=False, skip_on_failure=True)
    def check_new_passwords_match(cls, values):
        new_password = values.get('new_password')
        confirm_new_password = values.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise ValueError('New passwords do not match')
        return values