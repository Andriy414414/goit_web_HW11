from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str
    password: str = Field(min_length=6, max_length=800)



class UserResponse(UserSchema):
    id: int = 1
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)  # noqa


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: str
