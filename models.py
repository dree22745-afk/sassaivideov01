from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, default="")
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    model_used = Column(String, default="deepseek-chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    messages = relationship("Message", back_populates="conversation", cascade="all, delete")
    user = relationship("User", backref="conversations")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    model_used = Column(String)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")

class ErrorMemory(Base):
    __tablename__ = "error_memory"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_prompt = Column(Text)
    incorrect_response = Column(Text)
    corrected_response = Column(Text)
    error_type = Column(String(100))
    tech_stack = Column(String(255))
    embedding_keywords = Column(JSON)
    context_data = Column(JSON)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", backref="error_memories")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    rating = Column(String(10))
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", backref="feedbacks")

class SessionToken(Base):
    __tablename__ = "session_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(500), unique=True)
    token_type = Column(String(20), default="refresh")
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", backref="session_tokens")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, server_default=func.now())

class AudioTranscription(Base):
    __tablename__ = "audio_transcriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    audio_file_path = Column(String(500))
    transcript = Column(Text)
    language = Column(String(50))
    duration = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True)
    level = Column(String(20))
    module = Column(String(100))
    message = Column(Text)
    traceback = Column(Text)
    extra_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

Base.metadata.create_all(bind=engine)