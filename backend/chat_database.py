import datetime
from contextlib import contextmanager
from types import SimpleNamespace

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Text, event, Boolean
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import relationship, scoped_session, sessionmaker


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


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    instructions = Column(String)
    timestamp = Column(DateTime, index=True)
    chat = relationship("Chat", back_populates="agent", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    chat = relationship("Chat", back_populates="messages")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    timestamp = Column(DateTime, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id', ondelete='CASCADE'))
    agent = relationship("Agent", back_populates="chat", uselist=False)
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    settings = relationship("ChatSettings", back_populates="chat", uselist=False, cascade="all, delete-orphan")


class ChatSettings(Base):
    __tablename__ = 'chat_settings'
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True)
    max_tokens = Column(Integer, default=2048)
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    top_k = Column(Integer, default=0)
    min_p = Column(Float, default=0.0)
    typ_p = Column(Float, default=1.0)
    tfsz = Column(Float, default=1.0)
    rep_pen = Column(Float, default=1.2)
    rep_pen_range = Column(Integer, default=512)
    show_agent_instructions = Column(Boolean, default=True)
    chat = relationship("Chat", back_populates="settings")


class ChatDatabase:
    def __init__(self, db_url='sqlite:///chat_app.db'):
        self.engine = create_engine(db_url, echo=False)
        # Enable foreign key support for SQLite
        if 'sqlite' in db_url:
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))


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

    def add_agent(self, name, description, instructions):
        with self.session_scope() as session:
            new_agent = Agent(name=name, description=description, timestamp=datetime.datetime.now(),
                              instructions=instructions)
            session.add(new_agent)
            session.flush()
            return new_agent.id

    def update_agent(self, agent_id, name=None, description=None, instructions=None):
        with self.session_scope() as session:
            agent = session.query(Agent).get(agent_id)
            if agent:
                if name:
                    agent.name = name
                if description:
                    agent.description = description
                if instructions:
                    agent.instructions = instructions
            else:
                print("Agent not found.")

    def delete_agent(self, agent_id):
        with self.session_scope() as session:
            agent = session.query(Agent).get(agent_id)
            if agent:
                session.delete(agent)
            else:
                print("Agent not found.")

    def delete_message(self, message_id):
        with self.session_scope() as session:
            message = session.query(Message).filter(Message.id == message_id).first()
            if message:
                session.delete(message)
                return True
            else:
                print("Message not found.")
                return False

    def search_agents_by_name(self, name):
        with self.session_scope() as session:
            agents = session.query(Agent).filter(Agent.name.contains(name)).all()
            return agents

    def add_chat_with_agent_id(self, title, agent_id):
        with self.session_scope() as session:
            agent = session.query(Agent).get(agent_id)
            if agent:
                new_chat = Chat(title=title, timestamp=datetime.datetime.now(), agent_id=agent_id)
                session.add(new_chat)
                session.flush()
                return new_chat.id
            else:
                print("Agent not found.")
                return None

    def get_agent_by_id(self, agent_id):
        with self.session_scope() as session:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            return agent.to_obj() if agent else None

    def add_message(self, chat_id, role, content):
        with self.session_scope() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                new_message = Message(role=role, timestamp=datetime.datetime.now(), content=content, chat_id=chat_id)
                session.add(new_message)
                session.flush()
                return new_message.id, new_message.timestamp
            else:
                print("Chat not found.")
                return None

    def edit_message(self, message_id, content):
        with self.session_scope() as session:
            msg = session.query(Message).filter(Message.id == message_id).first()
            if msg:
                msg.content = content
                return True
            else:
                print("Message not found.")
                return None

    def set_chat_title(self, chat_id, title):
        with self.session_scope() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                chat.title = title
                return True
            else:
                print("Chat not found.")
                return None

    def search_chats_by_title(self, title):
        with self.session_scope() as session:
            chats = session.query(Chat).filter(Chat.title.contains(title)).all()
            return chats

    def search_messages_by_content(self, content):
        with self.session_scope() as session:
            messages = session.query(Message).filter(Message.content.contains(content)).all()
            return messages

    def get_all_agents(self):
        with self.session_scope() as session:
            agents = session.query(Agent).all()
            return [agent.to_obj() for agent in agents]

    def get_all_chats(self):
        with self.session_scope() as session:
            chats = session.query(Chat).all()
            return [chat.to_obj() for chat in chats]

    def get_all_messages_from_chat(self, chat_id):
        with self.session_scope() as session:
            messages = session.query(Message).filter(Message.chat_id == chat_id).all()
            return messages

    def delete_chat(self, chat_id):
        with self.session_scope() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                chat_settings = session.query(ChatSettings).filter(ChatSettings.chat_id == chat_id).first()
                if chat_settings:
                    session.delete(chat_settings)
                session.delete(chat)
            else:
                print("Chat not found.")

    def get_chat_details(self, chat_id):
        with self.session_scope() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                agent_details = {
                    "id": chat.agent.id,
                    "name": chat.agent.name,
                    "description": chat.agent.description,
                    "instructions": chat.agent.instructions
                } if chat.agent else None

                messages_details = [
                    {
                        "id": message.id,
                        "role": message.role,
                        "content": message.content,
                        "timestamp": message.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
                        "chat_id": chat_id
                    } for message in chat.messages
                ]

                if chat.settings is None:
                    chat.settings = ChatSettings(chat_id=chat_id)
                    session.add(chat.settings)
                    session.flush()

                settings = {
                    'max_tokens': chat.settings.max_tokens,
                    'temperature': chat.settings.temperature,
                    'top_p': chat.settings.top_p,
                    'top_k': chat.settings.top_k,
                    'min_p': chat.settings.min_p,
                    'typ_p': chat.settings.typ_p,
                    'tfsz': chat.settings.tfsz,
                    'rep_pen': chat.settings.rep_pen,
                    'rep_pen_range': chat.settings.rep_pen_range
                }

                chat_details = {
                    "id": chat_id,
                    "title": chat.title,
                    "timestamp": chat.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
                    "agent": agent_details,
                    "messages": messages_details,
                    "settings": settings
                }

                return chat_details

            else:
                return None

    def add_or_update_chat_settings(self, chat_id, settings_dict):
        with self.session_scope() as session:
            chat_settings = session.query(ChatSettings).filter_by(chat_id=chat_id).first()
            if not chat_settings:
                chat_settings = ChatSettings(chat_id=chat_id, **settings_dict)
                session.add(chat_settings)
            else:
                for key, value in settings_dict.items():
                    setattr(chat_settings, key, value)
            session.flush()
            return chat_settings

    def get_chat_settings(self, chat_id):
        with self.session_scope() as session:
            chat_settings = session.query(ChatSettings).filter_by(chat_id=chat_id).first()
            if not chat_settings:
                return ChatSettings(chat_id=chat_id)
            return chat_settings

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Session.remove()
        self.engine.dispose()


if __name__ == "__main__":
    with ChatDatabase() as db:
        db.add_agent("Helpful Assistant", "A helpful assistant", "You are a helpful assistant.")
