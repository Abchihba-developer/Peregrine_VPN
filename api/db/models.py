from api.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Wireguard(Base):
    __tablename__ = "wireguard"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    username: Mapped[str | None]
    private_key: Mapped[str]
    public_key: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, private_key={self.private_key!r}, public_key={self.public_key!r})"




