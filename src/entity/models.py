from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy import String


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    second_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(50), index=True)
    birthday: Mapped[Date] = mapped_column(Date)
    add_info: Mapped[str] = mapped_column(String(150))
