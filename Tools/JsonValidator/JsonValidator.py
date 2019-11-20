import sys
import click

from src.Validator import Validator

@click.command(context_settings={'help_option_names':['--help', '-h']})
@click.option('-v', '--verbose', count=True, help='verbosity to print')
def validate(verbose: int):
	"""
	This is the Command Line Interface of the JsonValidator for all Modules
	of Project Alice. Currently the following commands are supported.
	"""
	valid = Validator(verbosity=verbose)
	error = valid.validate()
	sys.exit(error)

	#click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
