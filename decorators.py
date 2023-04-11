from typing import Optional
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.interfaces.decorator import DecoratorInterface
from graia.broadcast.exceptions import ExecutionStop, RequirementCrashed
from graia.ariadne.model import Group, Member, MemberPerm

import yaml

from orm import *

with open('configs.yml', encoding='UTF-8') as f:
    ua = yaml.safe_load(f)['ultra_administration']

class ConfigCheck(Decorator):
    '''判断是否符合插件文件夹设置'''
    pre = True

    def __init__(self, folder, name, sche=False):
        self.folder = folder
        self.name   = name
        self.sche   = sche

    async def target(self, interface: DecoratorInterface):
        if self.sche:
            search = session.query(Module).filter_by(folder=self.folder, name=self.name).first()
            if not (search and search.switch):
                raise ExecutionStop
        else:
            dis = interface.dispatcher_interface
            try:
                group = (await dis.lookup_param("group", Group, None)).id
            except RequirementCrashed:
                group = None
            try:
                member = (await dis.lookup_param("member", Member, None)).id
            except RequirementCrashed:
                member = None

            filters = [
                Module.name == self.name,
                Module.folder == self.folder,
                ]
            if group:
                filters.append(ModuleSetting.group_id == group)

            search = session.query(ModuleSetting).join(Module).filter(*filters).first()

            if not (search and search.module.switch and search.switch):
                raise ExecutionStop

            search = session.query(QQGroup).filter_by(id=group).first()

            if search and member in search.black_list:
                raise ExecutionStop

class SettingCheck(Decorator):
    pre = True

    def __init__(self,
                 active_groups: Optional[list] = None,
                 negative_groups: Optional[list] = None,
                 active_members: Optional[list] = None,
                 negative_members: Optional[list] = None,
                 out_control: bool = True):
        self.active_groups = active_groups or []
        self.negative_groups = negative_groups or []
        self.active_members = active_members or []
        self.negative_members = negative_members or []
        self.out_control = out_control or []

    async def target(self, interface: DecoratorInterface):
        try:
            group = (await interface.dispatcher_interface.lookup_param("group", Group, None)).id
        except RequirementCrashed:
            group = None
        try:
            member = (await interface.dispatcher_interface.lookup_param("member", Member, None)).id
        except RequirementCrashed:
            member = None

        ag = self.active_groups
        ng = self.negative_groups
        am = self.active_members
        nm = self.negative_members

        if group:
            if ag and group not in ag:
                raise ExecutionStop()
            if ng and group in ng:
                raise ExecutionStop()
        
        if member:
            if am and member not in am:
                raise ExecutionStop()
            if nm and member in nm:
                raise ExecutionStop()

def config_check(
    active_groups: list = [],
    negative_groups: list = [],
    active_members: list = [],
    negative_members: list = []
    ):
    '''判断是否符合插件文件夹设置'''
    async def config_wrapper(group: Group, member: Member):
        ag = active_groups
        ng = negative_groups
        am = active_members
        nm = negative_members

        if any((
            ag and group.id not in ag,
            ng and group.id in ng,
            am and member.id not in am,
            nm and member.id in nm
            )):            raise ExecutionStop()

    return Depend(config_wrapper)

def admin_check():
    async def admin_wrapper(member: Member):
        '''判断是否为管理员/群主/'''
        if (member.permission not in [MemberPerm.Owner, MemberPerm.Administrator] and
            member.id not in ua
        ):
            raise ExecutionStop()
    return Depend(admin_wrapper)