
from pydrive.auth import GoogleAuth

# just a tiny layer of abstraction with this factory method
def create_authenticator(args):
	if args.auth_web:
		return WebAuthenticator()
	elif args.auth_conf is not None:
		return ConfigAuthenticator(args.auth_conf)
	else:
		return SimpleAuthenticator()

class SimpleAuthenticator(object):
	
	"""
	empty authenticator object
	in practice we 'll probably fallback to Google's default method when using this one
	"""

	def __init__(self):
		pass

	def authenticate(self):
		return None

class WebAuthenticator(SimpleAuthenticator):

	"""
	web based flow
	should pop-up default browser and block for action
	"""

	def __init__(self):
		super(WebAuthenticator, self).__init__()

	def authenticate(self):
		
		gauth = GoogleAuth()

		try:
			gauth.LocalWebserverAuth()  # Create local web-server and auto handles authentication.
			return gauth
		except Exception as ex:
			print "error during authentication: %s" % ex
			return None

class ConfigAuthenticator(SimpleAuthenticator):
	
	"""
	authenticate based on dedicated config file
	"""

	def __init__(self, conf_file):
		super(ConfigAuthenticator, self).__init__()
		self.conf_file = conf_file

	def authenticate(self):

		gauth = GoogleAuth()

		try:
			# Try to load saved client credentials
			gauth.LoadCredentialsFile(self.conf_file)

			if gauth.credentials is None:
				# Authenticate if they're not there
				gauth.LocalWebserverAuth()
			elif gauth.access_token_expired:
				# Refresh them if expired
				gauth.Refresh()
			else:
				# Initialize the saved creds
				gauth.Authorize()

			# Save the current credentials to a file
			gauth.SaveCredentialsFile(self.conf_file)

			return gauth

		except Exception as ex:
			print "error during authentication: %s" % ex
			return None
