import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class Base(DeclarativeBase):
    pass


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
                return file.id, file.path, file.content
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
            return [(file.id, file.path) for file in files]

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()
