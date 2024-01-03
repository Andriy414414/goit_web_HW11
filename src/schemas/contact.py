from pydantic import BaseModel, EmailStr, Field, PastDate, ConfigDict


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    second_name: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=50)
    birthday: PastDate
    add_info: str = Field(min_length=1, max_length=150)
    user_id: int
    model_config = ConfigDict(from_attributes=True)  # noqa


class ContactUpdateSchema(ContactSchema):
    completed: bool


class ContactResponse(ContactSchema):
    first_name: str
    second_name: str
    email: str
    birthday: PastDate
    add_info: str
    model_config = ConfigDict(from_attributes=True) # noqa
