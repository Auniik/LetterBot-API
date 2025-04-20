import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder


from sqlalchemy import Column, String, TIMESTAMP, BigInteger, Text, Boolean
from sqlalchemy.orm import validates
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import Base
from app.schema.settings import SettingUpdateDTO


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(BigInteger, primary_key=True)
    type = Column(String(50), default='string')
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

    @classmethod
    def get_settings_map(cls, session: AsyncSession, only_active: bool = True) -> dict:
        # query = session.query(cls)
        # if only_active:
        #     query = query.filter(cls.is_active.is_(True))
        # settings = query.all()
        # return dict({setting.key: setting.get_typed_value() for setting in settings})
        ...

    def get_typed_value(self):
        if self.value is None:
            return None
        if self.type == 'int':
            return int(self.value)
        elif self.type == 'bool':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.type == 'json':
            try:
                data = json.loads(self.value)
                return dict(data) if data is not None else None
            except json.JSONDecodeError:
                return None
        else:
            return self.value

    def set_typed_value(self, val):
        if isinstance(val, bool):
            self.value = str(val).lower()
            self.type = 'bool'
        elif isinstance(val, int):
            self.value = str(val)
            self.type = 'int'
        elif isinstance(val, dict) or isinstance(val, list):
            self.value = json.dumps(val)
            self.type = 'json'
        else:
            self.value = str(val)
            self.type = 'string'

    @validates('key')
    def validate_key(self, key, value):
        if not value:
            raise ValueError("Setting key cannot be empty.")
        return value



async def get_all_settings(db: AsyncSession):
    stmt = select(Setting).order_by(Setting.id)
    result = await db.execute(stmt)
    settings = result.scalars().all()

    return [
        {
            **jsonable_encoder(setting),
            "value": setting.get_typed_value()
        }
        for setting in settings
    ]

async def update_setting(
    db: AsyncSession,
    setting_id: int,
    new_value: SettingUpdateDTO
) -> Setting | None:
    stmt = select(Setting).where(Setting.id == setting_id)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    if setting:
        setting.type = new_value.type
        setting.set_typed_value(new_value.value)
        setting.is_active = new_value.is_active
        db.add(setting)
        await db.commit()
        await db.refresh(setting)

    return setting