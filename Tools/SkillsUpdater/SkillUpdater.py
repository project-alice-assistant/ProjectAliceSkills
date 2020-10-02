import click
import json
import os
import shutil
from Version import Version
from pathlib import Path

backupDir = Path(os.path.dirname(os.path.abspath(__file__)), 'backup')
skillRoot = Path('../../PublishedSkills/')


@click.group()
def cli():
	"""
	This script lets you update the skills in the published skill directory.
	It increments the target version number by 1
	TARGET can be either `hotfix`, `feature` or `major`
	Optionally you can specify an Alice min version to be set
	"""
	pass


@cli.command()
@click.option('-t', '--target', default='hotfix', help='hotfix, feature or major')
@click.option('-a', '--alicemin', help="If provided, sets Alice's min version")
@click.option('-b', '--backup', default=False, help="Make a backup of the install files first")
def update(target: str, alicemin: str, backup: bool):
	if target not in ['hotfix', 'feature', 'major']:
		click.echo("Only 'hotfix', 'feature' or 'major' supported for target")
		return

	if backup:
		if backupDir.exists():
			shutil.rmtree(backupDir)
		backupDir.mkdir()

	aliceMinVersion = Version.fromString(alicemin) if alicemin else None
	if aliceMinVersion and str(aliceMinVersion) == '0.0.0-0':
		click.echo('Invalid min alice version, aborting')
		return

	for installFile in skillRoot.glob('**/*.install'):

		if backup:
			shutil.copy(installFile, backupDir)

		data = json.loads(installFile.read_text())
		version = Version.fromString(data['version'])

		if target == 'hotfix':
			version.hotfix += 1
		elif target == 'feature':
			version.hotfix = 0
			version.updateVersion += 1
		elif target == 'major':
			version.hotfix = 0
			version.updateVersion = 0
			version.mainVersion += 1

		data['version'] = str(version)

		if aliceMinVersion:
			data['aliceMinVersion'] = str(aliceMinVersion)

		installFile.write_text(json.dumps(data, indent=4, ensure_ascii=False))
		click.echo(f'Rewritten "{installFile.stem}"')


@cli.command()
def revert():
	if not backupDir.exists():
		click.echo('No backup found')
		return

	for file in backupDir.glob('*.install'):
		shutil.copy(file, Path(skillRoot, file.stem, f'{file.stem}.install'))
		click.echo(f'Reverted {file.stem}')


@cli.command()
@click.argument('target', required=True)
@click.option('-b', '--backup', default=False, help="Make a backup of the install files first")
def droparg(target: str, backup: bool):
	if backup:
		if backupDir.exists():
			shutil.rmtree(backupDir)
		backupDir.mkdir()

	for installFile in skillRoot.glob('**/*.install'):
		if backup:
			shutil.copy(installFile, backupDir)

		data = json.loads(installFile.read_text())
		if target in data:
			del data[target]
			installFile.write_text(json.dumps(data, indent=4, ensure_ascii=False))
			click.echo(f'Dropped "{target}" from "{installFile.stem}"')


@cli.command()
@click.argument('target', required=True)
@click.argument('value', required=True)
@click.option('-b', '--backup', default=False, help="Make a backup of the install files first")
def addarg(target: str, value: str, backup: bool):
	if backup:
		if backupDir.exists():
			shutil.rmtree(backupDir)
		backupDir.mkdir()

	for installFile in skillRoot.glob('**/*.install'):
		if backup:
			shutil.copy(installFile, backupDir)

		data = json.loads(installFile.read_text())
		if target not in data:
			data[target] = value
			installFile.write_text(json.dumps(data, indent=4, ensure_ascii=False))
			click.echo(f'Added "{target} = {value}" to "{installFile.stem}"')


if __name__ == '__main__':
	cli()
