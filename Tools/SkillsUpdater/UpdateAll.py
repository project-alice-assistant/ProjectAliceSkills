from glob import glob

import click
from typing import Union

from ProjectAliceSK.util.Helpers import OptionEatAll


@click.command()
@click.option('-v', '--version', default='hotfix', cls=OptionEatAll, help='hotfix, feature, release')
@click.option('-am', '--aliceMin', default=False, cls=OptionEatAll, help='Set a minimum Alice version number')
def updateAll(version: str, aliceMin: Union[bool, str]):
	"""
	Update all skill install files
	:param version: Which version should be increased
	:param aliceMin: If alice min needs updating
	:return:
	"""
	for installFile in glob('../../PublishedSkills/*'):
		print(installFile)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	updateAll()
