from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    instructions = Column(String)
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

    def add_agent(self, name, instructions):
        session = self.Session()
        new_agent = Agent(name=name, instructions=instructions)
        session.add(new_agent)
        session.commit()
        return new_agent.id

    def update_agent(self, agent_id, name=None, instructions=None):
        session = self.Session()
        agent = session.query(Agent).get(agent_id)
        if agent:
            if name:
                agent.name = name
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
            new_chat = Chat(title=title, agent=agent)
            session.add(new_chat)
            session.commit()
            return new_chat.id
        else:
            print("Agent not found.")
            return None

    def add_chat(self, title, agent_name, agent_instructions):
        agent_id = self.add_agent(agent_name, agent_instructions)
        return self.add_chat_with_agent_id(title, agent_id)

    def add_message(self, chat_title, role, content):
        session = self.Session()
        chat = session.query(Chat).filter(Chat.title == chat_title).first()
        if chat:
            new_message = Message(role=role, content=content, chat=chat)
            session.add(new_message)
            session.commit()
            return new_message.id
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


# Example usage:
db = ChatDatabase()

# Add a chat
db.add_agent("Jack", "You are a helpful assistant.")