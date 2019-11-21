import sys
import click

from src.Validator import Validator
from src.Helpers import OptionEatAll

@click.command(context_settings={'help_option_names':['--help', '-h']})
@click.option('--paths', cls=OptionEatAll, required=True, help='module paths to test')
@click.option('-v', '--verbose', count=True, help='verbosity to print')
@click.option('--token', help='github token')
def validate(paths: list, verbose: int, token: str):
	"""
	This is the Command Line Interface of the JsonValidator for all Modules
	of Project Alice. Currently the following commands are supported.
	"""
	username = 'ProjectAlice'
	if not token:
		username = click.prompt('Github username')
		token = click.prompt('Github password', hide_input=True, confirmation_prompt=True)

	valid = Validator(
		modulePaths=paths,
		verbosity=verbose,
		username=username,
		token=token)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
