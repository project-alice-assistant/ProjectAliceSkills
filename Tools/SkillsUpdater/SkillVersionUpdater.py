import click

from Tools.SkillsUpdater import UpdateAll


@click.group()
def cli():
	"""
	This is the Command Line Interface of the Project Alice Skill Kit.
	Currently the following commands are supported.
	"""
	pass


cli.add_command(UpdateAll)

if __name__ == '__main__':
	cli()
