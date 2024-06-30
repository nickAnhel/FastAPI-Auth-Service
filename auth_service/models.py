from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        res = []
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                res.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(res)})"
