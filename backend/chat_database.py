import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
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
            return new_message.id
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
                    "chat_id": chat_id
                } for message in chat.messages
            ]

            chat_details = {
                "id": chat_id,
                "title": chat.title,
                "timestamp": chat.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
                "agent": agent_details,
                "messages": messages_details
            }

            return chat_details

        else:
            return None


if "__main__" == __name__:
    db = ChatDatabase()
    db.add_agent("Helpful Assistant", "A helpful assistant", "You are a helpful assistant.")
