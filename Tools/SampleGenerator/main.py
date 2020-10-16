import json

import click
from pathlib import Path

skillRoot = Path('../../PublishedSkills/')


@click.group()
def cli():
	"""
	This script generates samples for skill dialogs
	"""
	pass


@cli.command()
def generate():
	for dialogTemplate in skillRoot.rglob('dialogTemplate/*.json'):
		if Path(dialogTemplate.parent, f'{dialogTemplate.stem}.sample').exists():
			continue

		sample = dict()
		data = json.loads(dialogTemplate.read_text(encoding='utf-8'))
		for intent in data['intents']:
			if not intent['enabledByDefault']:
				continue
			sample[intent['name']] = list()

		Path(dialogTemplate.parent, f'{dialogTemplate.stem}.sample').write_text(json.dumps(sample, ensure_ascii=False, indent=4))
		print(f'Generated samples file for skill {dialogTemplate.parent.parent.stem} in "{dialogTemplate.stem}"')


if __name__ == '__main__':
	cli()
