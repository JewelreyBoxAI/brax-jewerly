from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import Base

class Thread(Base):
    __tablename__ = "threads"
    id = Column(Text, primary_key=True)
    user_id = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(BigInteger, primary_key=True)
    thread_id = Column(Text, ForeignKey("threads.id", ondelete="CASCADE"))
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    thread = relationship("Thread", back_populates="messages")
    embedding = relationship("MsgEmbedding", uselist=False, back_populates="message", cascade="all, delete-orphan")

class MsgEmbedding(Base):
    __tablename__ = "msg_embeddings"
    msg_id = Column(BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(1536))
    message = relationship("Message", back_populates="embedding")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(BigInteger, primary_key=True)
    thread_id = Column(Text, nullable=True)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    intent = Column(Text)
    notes = Column(Text)
    raw = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())