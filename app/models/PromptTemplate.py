from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import Base
from app.schema.prompt_template import PromptTemplateDTO


class PromptTemplate(Base):
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    template = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    category = Column(String, nullable=True)


async def get_all_prompt_templates(db: AsyncSession):
    builder = select(PromptTemplate).order_by(PromptTemplate.type)
    result = await db.execute(builder)
    return result.scalars().all()

async def get_prompt_template(db: AsyncSession, template_id: int):
    builder = select(PromptTemplate).where(PromptTemplate.id == template_id)
    result = await db.execute(builder)
    return result.scalars().first()

async def save_prompt_template(db: AsyncSession, attributes: PromptTemplateDTO):
    prompt_template = PromptTemplate(**attributes.model_dump())
    db.add(prompt_template)
    await db.commit()
    return prompt_template

async def update_prompt_template(db: AsyncSession, id: int, attributes: PromptTemplateDTO):
    builder = select(PromptTemplate).where(PromptTemplate.id == id)
    result = await db.execute(builder)
    prompt_template = result.scalars().first()
    if prompt_template:
        for key, value in attributes.model_dump().items():
            setattr(prompt_template, key, value)
        db.add(prompt_template)
        await db.commit()
        return prompt_template
    return None

async def delete_prompt_template(db: AsyncSession, id: int):
    builder = select(PromptTemplate).where(PromptTemplate.id == id)
    result = await db.execute(builder)
    prompt_template = result.scalars().first()
    if prompt_template:
        await db.delete(prompt_template)
        await db.commit()
        return True
    return False