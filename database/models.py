from sqlalchemy import Column , Integer, String , Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ =  'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column( DateTime, default=datetime.datetime.utcnow)
    
    #relationships
    sessions = relationship("Session",  back_populates="user", cascade="all, delete-orphan")
    prompt_templates = relationship("PromptTemplate", back_populates="user", cascade="all, delete-orphan")

   
class Session(Base):
    __tablename__ =  'sessions'
    id = Column(Integer, primary_key=True)
    user_id= Column(Integer, ForeignKey('users.id'))
    name=Column(String(100), nullable=False)
    created_at = Column( DateTime, default=datetime.datetime.utcnow)
    last_accessed = Column( DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    
    
    #relationships
    users = relationship("User",  back_populates="sessions")
    messages = relationship("Message", back_populates="session",cascade="all, delete-orphan" )
    documents= relationship("Document", back_populates="session", cascade="all, delete-orphan")
    

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    role = Column(String(20), nullable=False)  # 'user', 'code_agent', 'doc_agent'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="messages")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'pdf', 'xlsx', 'txt', etc.
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="documents")

class PromptTemplate(Base):
    __tablename__ = 'prompt_templates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False)
    agent_type = Column(String(20), nullable=False)  # 'code_agent', 'doc_agent'
    template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="prompt_templates")
    
