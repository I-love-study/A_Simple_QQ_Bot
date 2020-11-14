from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.group import Group, Member, MemberPerm
from .modules import plugin_dir_setting


def group_check(name, include = None, exclude = None):
	def group_wrapper(group: Group):
		'''判断是否在/不在群内
		支持手动输入和全局(core.trans())(手动优先级大于全局)'''
		active = include or [plugin_dir.active_groups
							 for plugin_dir in plugin_dir_setting 
							 if plugin_dir.dir_name in name][0]
		negative = exclude or [plugin_dir.negative_groups
							   for plugin_dir in plugin_dir_setting 
							   if plugin_dir.dir_name in name][0]
		if active:
			if group.id not in active:
				raise ExecutionStop()
		if negative:
			if group.id in negative:
				raise ExecutionStop()
	return Depend(group_wrapper)

def admin_check():
	def admin_wrapper(member: Member):
		'''判断是否为管理员/群主'''
		if member.permission not in [MemberPerm.Owner, MemberPerm.Administrator]:
			raise ExecutionStop()
	return Depend(admin_wrapper)

def member_check(include = None, exclude = None):
	def member_wrapper(member: Member):
		'''判断是否是某个群友发送
		支持手动输入和全局(core.trans())(手动优先级大于全局)'''
		active = include or [plugin_dir.active_members
							 for plugin_dir in plugin_dir_setting 
							 if plugin_dir.dir_name in name][0]
		negative = exclude or [plugin_dir.negative_members
							   for plugin_dir in plugin_dir_setting 
							   if plugin_dir.dir_name in name][0]
		if active:
			if member.id not in active:
				raise ExecutionStop()
		if negative:
			if member.id in negative:
				raise ExecutionStop()
	return Depend(member_wrapper)