
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, ForeignKey,DateTime,DATE
from config import DATABASE_URL
import datetime 
from datetime import datetime

engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)




class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    tg_id = Column(BigInteger, unique=True)
    date = Column(DATE, default=datetime.now)
    is_admin=Column(Boolean,default=False)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name_course=Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Task(Base):
    __tablename__ = 'tasks'

    id=Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id=Column(Integer, ForeignKey('courses.id'))
    title=Column(String)
    answer = Column(String) 
    created_at = Column(DateTime, default=datetime.now)


class Student(Base):
    __tablename__ = 'students' 
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))

class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    description = Column(String) 
    created_at = Column(DateTime, default=datetime.now)