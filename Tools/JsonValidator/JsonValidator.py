import sys
import click

from src.Validator import Validator

@click.command(context_settings={'help_option_names':['--help', '-h']})
@click.option('-v', '--verbose', count=True, help='verbosity to print')
@click.option('--token', help='github token')
def validate(verbose: int, token: str):
	"""
	This is the Command Line Interface of the JsonValidator for all Modules
	of Project Alice. Currently the following commands are supported.
	"""
	username = 'ProjectAlice'
	if not token:
		username = click.prompt('Github username')
		token = click.prompt('Github password', hide_input=True, confirmation_prompt=True)

	valid = Validator(
		verbosity=verbose,
		username=username,
		token=token)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
