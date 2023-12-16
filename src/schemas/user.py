from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(UserSchema):
    id: int = 1
    username: str
    email: str

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
