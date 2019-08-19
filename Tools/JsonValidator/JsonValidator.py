from src.validator import validator
import sys
import argparse

parser = argparse.ArgumentParser(description='decide which files to validate')	
parser.add_argument('--all', help='run all validation tasks', action='store_true')	
parser.add_argument('--install', help='validate installers', action='store_true')	
parser.add_argument('--dialog', help='validate dialog files', action='store_true')	
parser.add_argument('--talk', help='validate talk files', action='store_true')
parser.add_argument('--quiet', help='validate talk files', action='store_true')	


if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)
args = parser.parse_args()

installer = False
dialog = False
talk = False
warnings = True

if args.all:
	installer = True
	dialog = True
	talk = True

if args.install:
	installer = True
if args.dialog:
	dialog = True
if args.talk:
	talk = True
if args.quiet:
	warnings = False


valid = validator(installer=installer, dialog=dialog, talk=talk, warnings=warnings)
error = valid.validate()
valid.printResult()
sys.exit(error)