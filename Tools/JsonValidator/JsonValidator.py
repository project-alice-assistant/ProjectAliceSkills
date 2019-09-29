import sys
import click

from src.Validator import Validator

@click.command(context_settings={'help_option_names':['--help', '-h']})
@click.option('--all', '-a', 'allOpt', is_flag=True, help='run all validation tasks')
@click.option('--install', '-i', is_flag=True, help='validate installers')
@click.option('--dialog', '-d', is_flag=True, help='validate dialog files')
@click.option('--talk', '-t', is_flag=True, help='validate files')
@click.option('-v', '--verbose', count=True, help='verbosity to print')
def validate(allOpt: bool, install: bool, dialog: bool, talk: bool, verbose: int):
	"""
	This is the Command Line Interface of the JsonValidator for all Modules
	of Project Alice. Currently the following commands are supported.
	"""
	if allOpt:
		install = dialog = talk = True
	if True in (install, dialog, talk):
		valid = Validator(installer=install, dialog=dialog, talk=talk, verbosity=verbose)
		error = valid.validate()
		valid.printResult()
		sys.exit(error)
	else:
		click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
