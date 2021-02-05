from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.group import Group, Member, MemberPerm
from .modules import plugin_dir_setting


def get_plugin_setting(name):
	for plugin_dir in plugin_dir_setting:
		load = plugin_dir.dir_name.split('.')
		if load == name.split('.')[:len(load)]:
			return plugin_dir
	return None

def config_check(name,    
	active_groups: list = [],
    negative_groups: list = [],
    active_members: list = [],
    negative_members: list = []
    ):
	'''判断是否符合插件文件夹设置'''
	def config_wrapper(group: Group, member: Member):
		setting = get_plugin_setting(name)
		ag = active_groups or setting.active_groups
		ng = negative_groups or setting.negative_groups
		am = active_members or setting.active_members
		nm = negative_members or setting.negative_members

		if any((
			ag and group.id not in ag,
			ng and group.id in ng,
			am and member.id not in am,
			nm and member.id in nm
			)):raise ExecutionStop()

	return Depend(config_wrapper)

def admin_check():
	def admin_wrapper(member: Member):
		'''判断是否为管理员/群主'''
		if member.permission not in [MemberPerm.Owner, MemberPerm.Administrator]:
			raise ExecutionStop()
	return Depend(admin_wrapper)