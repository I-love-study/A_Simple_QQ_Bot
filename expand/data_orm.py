from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, JSON, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import insert

from typing import Union
from graia.application.group import Member
import ujson as json

Base = declarative_base()
    

#能够检测到Dict有修改的类
MDICT = MutableDict.as_mutable(JSON)
MLIST = MutableList.as_mutable(JSON)

class MemberInfo(Base):
    "用户信息"
    __tablename__ = 'MemberInfo'

    member                = Column(Integer, primary_key=True)

    coin                  = Column(Integer, comment="商城金币", default=0)
    lottery               = Column(Integer, comment="抽奖券"  , default=0)
    experience            = Column(MDICT  , comment="经验"    , default={})
    rank                  = Column(String , comment="佩戴头衔")
    avatar_frame          = Column(String , comment="佩戴头像框")
    divination_card       = Column(String , comment="装备卡罗牌")

    equip_rank            = Column(MLIST  , comment="已有头衔"  ,default=[])
    equip_avatar_frame    = Column(MLIST  , comment="已有头像框",default=[])
    equip_divination_card = Column(MLIST  , comment="已有卡罗牌",default=[])

    last_sign_in          = Column(MDICT  , comment="上次签到日期(Dict[timestamp])", default={})
    last_love_token       = Column(MDICT  , comment="上次上上签日期", default={})
    last_divination       = Column(Date   , comment="上次卡罗牌日期")
    last_lottery          = Column(Date   , comment="上次获取抽奖券日期")

    cumulative_love_token = Column(MDICT  , comment="累计上上签(good, soso, bad)", default={})

    def get(self, attr, default):
        if (value := getattr(self, attr)) is not None:
            return value
        else:
            return default

engine = create_engine('sqlite:///data/data.db?check_same_thread=False',
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False))
Base.metadata.create_all(engine, checkfirst=True)
session = sessionmaker(bind=engine)()



def make_sure(member: Union[int, Member]):
    stmt = insert(MemberInfo).values(
        member=member.id if isinstance(member, Member) else member
        ).on_conflict_do_nothing(index_elements=['member'])
    session.execute(stmt)

def select_member(member: Union[int, Member]):
    make_sure(member)
    return session.query(MemberInfo).filter_by(
        member=member.id if isinstance(member, Member) else member).first()

__all__ = ["MemberInfo", "session", "make_sure", "select_member"]