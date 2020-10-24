from graia.broadcast.exceptions import ExecutionStop
from graia.application.group import Group, Member, MemberPerm
from core import get

active_groups = get.trans('active_groups')

def active_check_message(group: Group):#判断群(消息来临)
	if group.id not in active_groups:
		raise ExecutionStop()

def active_check_in(member: Member):#判断群(入群/出群)
	if member.group.id not in active_groups:
		raise ExecutionStop()

def admin_check(member: Member):#判断权限
    if member.permission not in [MemberPerm.Owner, MemberPerm.Administrator]:
        raise ExecutionStop()