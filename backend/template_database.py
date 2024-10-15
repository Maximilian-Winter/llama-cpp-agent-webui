import datetime
import enum
from contextlib import contextmanager
from types import SimpleNamespace

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, declared_attr, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_obj(self):
        return SimpleNamespace(**self.to_dict())


class TemplateType(enum.Enum):
    USER_MESSAGE = "user_message"
    RAG_USER_MESSAGE = "rag_user_message"
    FILE_COMBINING = "file_combining"
    FILE_OUTPUT = "file_output"


class Template(Base):
    __tablename__ = 'templates'

    id = Column(Integer, primary_key=True)
    template_type = Column(String)
    template_name = Column(String)
    description = Column(String)
    content = Column(Text)


class TemplateSet(Base):
    __tablename__ = 'template_sets'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    user_message_template_id = Column(Integer, ForeignKey('templates.id'))
    rag_user_message_template_id = Column(Integer, ForeignKey('templates.id'))
    file_combining_template_id = Column(Integer, ForeignKey('templates.id'))
    file_output_template_id = Column(Integer, ForeignKey('templates.id'))

    user_message_template = relationship("Template", foreign_keys=[user_message_template_id])
    rag_user_message_template = relationship("Template", foreign_keys=[rag_user_message_template_id])
    file_combining_template = relationship("Template", foreign_keys=[file_combining_template_id])
    file_output_template = relationship("Template", foreign_keys=[file_output_template_id])


class TemplateManager:
    def __init__(self, db_url='sqlite:///persistent_templates.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_template(self, template_type: TemplateType, template_name: str, description: str, content: str):
        with self.session_scope() as session:
            template = Template(template_type=template_type.value, template_name=template_name, description=description, content=content)
            session.add(template)
        return template

    def get_template(self, template_id: int):
        with self.session_scope() as session:
            template = session.query(Template).filter_by(id=template_id).first()
            if template:
                return template.to_obj()
            else:
                return None

    def get_all_templates(self):
        with self.session_scope() as session:
            templates = session.query(Template).all()
            return [template.to_obj() for template in templates]

    def get_all_templates_filtered_by_type(self, template_type: TemplateType):
        with self.session_scope() as session:
            templates = session.query(Template).filter_by(template_type=template_type.value).all()
            return [template.to_obj() for template in templates]

    def update_template(self, template_id, template_type: TemplateType = None, template_name: str = None, description=None, content: str = None):
        with self.session_scope() as session:
            template = session.query(Template).filter_by(id=template_id).first()
            if template:
                if template_name is not None:
                    template.template_name = template_name
                if content is not None:
                    template.content = content
                if description is not None:
                    template.description = description
                if template_type is not None:
                    template.template_type = template_type.value
            else:
                raise ValueError(f"Template with id {template_id} not found.")

    def delete_template(self, template_id):
        with self.session_scope() as session:
            template = session.query(Template).filter_by(id=template_id).first()
            if template:
                session.delete(template)
                return True
            return False

    def add_template_set(self, name: str, description: str, user_message_id: int, rag_user_message_id: int, file_combining_id: int, file_output_id: int):
        with self.session_scope() as session:
            template_set = TemplateSet(
                name=name,
                description=description,
                user_message_template_id=user_message_id,
                rag_user_message_template_id=rag_user_message_id,
                file_combining_template_id=file_combining_id,
                file_output_template_id=file_output_id
            )
            session.add(template_set)
        return template_set

    def get_template_set(self, template_set_id: int):
        with self.session_scope() as session:
            template_set = session.query(TemplateSet).filter_by(id=template_set_id).first()
            if template_set:
                return template_set.to_obj()
            else:
                return None

    def get_all_template_sets(self):
        with self.session_scope() as session:
            template_sets = session.query(TemplateSet).all()
            return [template_set.to_obj() for template_set in template_sets]

    def update_template_set(self, template_set_id: int, **kwargs):
        with self.session_scope() as session:
            template_set = session.query(TemplateSet).filter_by(id=template_set_id).first()
            if template_set:
                for key, value in kwargs.items():
                    setattr(template_set, key, value)
            else:
                raise ValueError(f"TemplateSet with id {template_set_id} not found.")

    def delete_template_set(self, template_set_id: int):
        with self.session_scope() as session:
            template_set = session.query(TemplateSet).filter_by(id=template_set_id).first()
            if template_set:
                session.delete(template_set)
                return True
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()