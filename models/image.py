from datetime import datetime
from sqlmodel import SQLModel, Field, Session


class ImageMetadata(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    media_path: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )

    def save(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)
