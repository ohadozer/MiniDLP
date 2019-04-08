from argparse import ArgumentParser
from Authenticators import *
from DriveClient import *
from DLPEngine import  *

def parse_args():

	"""
	parse command line arguments.
	file-id is mandatory
	"""

	parser = ArgumentParser(prog="Mini-DLP")

	parser.add_argument("-i", "--file-id", dest="file_id", help="file id of the file to scan", required=True)
	parser.add_argument("-s", "--non-parallel-mode", dest="parallel", action="store_false", default=True, help="force a non parallel mode")
	parser.add_argument("-c", "--chunk_size", dest="chunk_size", type=int, default=0, help="scan file in chunks (might be risky..)")

	auth_group = parser.add_mutually_exclusive_group()
	auth_group.add_argument("--auth-web", dest="auth_web", action="store_true", default=False, help="use web flow authentication")
	auth_group.add_argument("--auth-config", dest="auth_conf", type=str, default=None, help="use authentication config file (i.e. mycreds.json)")

	return parser.parse_args()

def main():

	"""
	entry point
	"""

	# command line arguments
	args = parse_args()

	# authentication ?
	authenticator = create_authenticator(args)
	auth_object = authenticator.authenticate()

	# create a Drive client
	drive_client = DriveClient(auth_object)

	# start engine
	engine = DLPEngine(drive_client, args.parallel)
	engine.go(args.file_id, args.chunk_size)

if __name__ == '__main__':
	main()