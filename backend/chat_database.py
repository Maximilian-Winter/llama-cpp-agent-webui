import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    instructions = Column(String)
    timestamp = Column(DateTime, index=True)
    chat = relationship("Chat", back_populates="agent", uselist=False)


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    chat = relationship("Chat", back_populates="messages")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    timestamp = Column(DateTime, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    agent = relationship("Agent", back_populates="chat", uselist=False)
    messages = relationship("Message", back_populates="chat")
    settings = relationship("ChatSettings", back_populates="chat", uselist=False)


class ChatSettings(Base):
    __tablename__ = 'chat_settings'
    chat_id = Column(Integer, ForeignKey('chats.id'), primary_key=True)
    max_tokens = Column(Integer, default=2048)
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    top_k = Column(Integer, default=0)
    min_p = Column(Float, default=0.0)
    typ_p = Column(Float, default=1.0)
    tfsz = Column(Float, default=1.0)
    rep_pen = Column(Float, default=1.2)
    rep_pen_range = Column(Integer, default=512)
    chat = relationship("Chat", back_populates="settings")


class ChatDatabase:
    def __init__(self, db_url='sqlite:///chat_app.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def add_agent(self, name, description, instructions):
        session = self.Session()
        new_agent = Agent(name=name, description=description, timestamp=datetime.datetime.now(),
                          instructions=instructions)
        session.add(new_agent)
        session.commit()
        return new_agent.id

    def update_agent(self, agent_id, name=None, description=None, instructions=None):
        session = self.Session()
        agent = session.query(Agent).get(agent_id)
        if agent:
            if name:
                agent.name = name
            if description:
                agent.description = description
            if instructions:
                agent.instructions = instructions
            session.commit()
        else:
            print("Agent not found.")

    def delete_agent(self, agent_id):
        session = self.Session()
        agent = session.query(Agent).get(agent_id)
        if agent:
            session.delete(agent)
            session.commit()
        else:
            print("Agent not found.")

    def delete_message(self, message_id):
        session = self.Session()
        message = session.query(Message).filter(Message.id == message_id).first()
        if message:
            session.delete(message)
            session.commit()
            return True
        else:
            print("Message not found.")
            return False

    def search_agents_by_name(self, name):
        session = self.Session()
        agents = session.query(Agent).filter(Agent.name.contains(name)).all()
        return agents

    def add_chat_with_agent_id(self, title, agent_id):
        session = self.Session()
        agent = session.query(Agent).get(agent_id)
        if agent:
            new_chat = Chat(title=title, timestamp=datetime.datetime.now(), agent_id=agent_id)
            session.add(new_chat)
            session.commit()
            return new_chat.id
        else:
            print("Agent not found.")
            return None

    def get_agent_by_id(self, agent_id):
        session = self.Session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        return agent

    def add_message(self, chat_id, role, content):
        session = self.Session()
        chat = session.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            new_message = Message(role=role, timestamp=datetime.datetime.now(), content=content, chat_id=chat_id)
            session.add(new_message)
            session.commit()
            return new_message.id, new_message.timestamp
        else:
            print("Chat not found.")
            return None

    def edit_message(self, message_id, content):
        session = self.Session()
        msg = session.query(Message).filter(Message.id == message_id).first()
        if msg:
            msg.content = content
            session.commit()
            return True
        else:
            print("Chat not found.")
            return None

    def set_chat_title(self, chat_id, title):
        session = self.Session()
        chat = session.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.title = title
            session.commit()
            return True
        else:
            print("Chat not found.")
            return None

    def search_chats_by_title(self, title):
        session = self.Session()
        chats = session.query(Chat).filter(Chat.title.contains(title)).all()
        return chats

    def search_messages_by_content(self, content):
        session = self.Session()
        messages = session.query(Message).filter(Message.content.contains(content)).all()
        return messages

    def get_all_agents(self):
        session = self.Session()
        agents = session.query(Agent).all()
        return agents

    def get_all_chats(self):
        session = self.Session()
        chats = session.query(Chat).all()
        return chats

    def get_all_messages_from_chat(self, chat_id):
        session = self.Session()
        messages = session.query(Message).filter(Message.chat_id == chat_id).all()
        return messages

    def delete_chat(self, chat_id):
        session = self.Session()
        chat = session.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat_settings = session.query(ChatSettings).filter(ChatSettings.chat_id == chat_id).first()
            if chat_settings:
                session.delete(chat_settings)
                session.commit()
            session.delete(chat)
            session.commit()
        else:
            print("Chat not found.")

    def get_chat_details(self, chat_id):
        session = self.Session()
        chat = session.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            # Assuming the agent is linked directly to the chat
            agent_details = {
                "id": chat.agent.id,
                "name": chat.agent.name,
                "description": chat.agent.description,
                "instructions": chat.agent.instructions
            } if chat.agent else None

            # Compiling a list of messages in the chat
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
                session.commit()

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
        session = self.Session()
        chat_settings = session.query(ChatSettings).filter_by(chat_id=chat_id).first()
        if not chat_settings:
            chat_settings = ChatSettings(chat_id=chat_id, **settings_dict)
            session.add(chat_settings)
        else:
            for key, value in settings_dict.items():
                setattr(chat_settings, key, value)
        session.commit()
        return chat_settings

    def get_chat_settings(self, chat_id):
        session = self.Session()
        chat_settings = session.query(ChatSettings).filter_by(chat_id=chat_id).first()
        if not chat_settings:
            # Return default settings if not found
            return ChatSettings(chat_id=chat_id)
        return chat_settings


if "__main__" == __name__:
    db = ChatDatabase()
    db.add_agent("Helpful Assistant", "A helpful assistant", "You are a helpful assistant.")
