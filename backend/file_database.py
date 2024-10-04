import datetime
from contextlib import contextmanager
from types import SimpleNamespace

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, declared_attr
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


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


class FileManager:
    def __init__(self, db_url='sqlite:///persistent_files.db'):
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

    def add_file(self, path, content):
        with self.session_scope() as session:
            file = File(path=path, content=content)
            session.add(file)
            try:
                session.commit()
                return file.id
            except IntegrityError:
                session.rollback()
                raise ValueError(f"File with path '{path}' already exists.")

    def get_file(self, file_id):
        with self.session_scope() as session:
            file = session.query(File).filter_by(id=file_id).first()
            if file:
                return file.to_obj()
            else:
                return None

    def get_file_by_path(self, file_path):
        with self.session_scope() as session:
            file = session.query(File).filter_by(path=file_path).first()
            if file:
                return file.id, file.path, file.content
            else:
                return None

    def get_all_file_paths(self):
        with self.session_scope() as session:
            files = session.query(File).all()
            return [file.to_obj() for file in files]

    def get_all_files(self):
        with self.session_scope() as session:
            files = session.query(File).all()
            return [(file.id, file.path, file.content) for file in files]

    def update_file(self, file_id, content):
        with self.session_scope() as session:
            file = session.query(File).filter_by(id=file_id).first()
            if file:
                file.content = content
            else:
                raise ValueError(f"File with id {file_id} not found.")

    def delete_file(self, file_id):
        with self.session_scope() as session:
            file = session.query(File).filter_by(id=file_id).first()
            if file:
                session.delete(file)
                return True
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()
