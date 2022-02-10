from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class QQGroup(Base):
    """QQ群"""
    __tablename__ = 'QQgroup'

    id         = Column(Integer, nullable=False, primary_key=True)
    black_list = Column(JSON, default=[])
    Permission = Column(String, default='ultra_administration')
    setting    = relationship("ModuleSetting", back_populates="QQgroup")

class Module(Base):
    """模组"""
    __tablename__ = 'module'

    id      = Column(Integer, primary_key=True)
    folder  = Column(String, nullable=False)
    name    = Column(String, nullable=False)
    switch  = Column(Boolean, default=True)
    setting = relationship("ModuleSetting", back_populates="module")

class ModuleSetting(Base):
    """模组设置(开启/关闭的群/人员)"""
    __tablename__ = 'module_setting'

    group_id  = Column(Integer, ForeignKey('QQgroup.id'), primary_key=True)
    module_id = Column(Integer, ForeignKey('module.id') , primary_key=True)
    switch    = Column(Boolean, nullable=False, default=True)
    QQgroup   = relationship("QQGroup", back_populates="setting")
    module    = relationship("Module" , back_populates="setting")

engine = create_engine('sqlite:///data/setting.db?check_same_thread=False')
Base.metadata.create_all(engine, checkfirst=True)
session = sessionmaker(bind=engine)()

