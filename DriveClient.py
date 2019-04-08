import requests
from pydrive.drive import GoogleDrive


class DriveClientStreamHandler(object):

	"""
	interface defining the behavior of handling Drive stream events
	"""

	def __init__(self):
		pass
		
	def new_line_callback(self, line_index, line):
		raise NotImplementedError("must be implemented in concrete class")

	def new_chunk_callback(self, buffer):
		raise NotImplementedError("must be implemented in concrete class")

	def stream_process_started(self, file_title):
		raise NotImplementedError("must be implemented in concrete class")

class DriveClient(object):

	"""
	a client for extracting binary content from drive hosted files
	content can be extraced in several methods
	"""

	def __init__(self, auth_object):
		self.auth = auth_object

	def _get_file_metadata(self, file_id):

		if not file_id or not isinstance(file_id, basestring):
			print "Error :: invalid file ID"
			return None, None

		drive = GoogleDrive(self.auth)
		file = drive.CreateFile({'id': file_id})
		file.FetchMetadata(fields='title, webContentLink')
		
		title = file['title']
		dl_link = file['webContentLink']

		if dl_link:
			return title, dl_link
		else:
			print "Error :: couldn't resolve file metadata"
			return None, None

	def get_content(self, file_id):

		"""
		return all content (string) at once
		"""

		title, dl_link = self._get_file_metadata(file_id)

		if dl_link:
			with requests.get(dl_link, stream=True) as response:
				if response and response.ok:  # basically means HTTP status < 400
					return title, response.text
				else:
					return None
		else:
			return None

	def get_stream(self, file_id, chunk_size=None):

		"""
		requests the content of a file and returns a stream of
		lines which is an iterable generator (can be consumed via 'for x in y')
		stream is lazy, meaning once it'll be returned (yielded) back its not guaranteed to hold all lines in memory.
		on the other hand, the caller can already start consuming what's been downloaded
		"""

		title, dl_link = self._get_file_metadata(file_id)

		if dl_link:
			with requests.get(dl_link, stream=True) as response:
				if response and response.ok:  # basically means HTTP status < 400
					if chunk_size:
						for chunk in response.iter_content(chunk_size=chunk_size):
							if chunk:
								yield title, chunk
					else:
						line_index = 0
						for line in response.iter_lines(chunk_size=chunk_size):
							if line:
								yield title, line_index, line
								line_index += 1
				else:
					print "Error :: request for stream of lines has failed"

	def process_stream(self, file_id, handler, chunk_size=None):
		
		"""
		requests the a content of a file from Drive, and handles it in a non-blocking like way.
		meaning a request resulting with a large response will be processed line by line, so while
		http content being currently downloded won't delay an already downloaded content from being processed.
		the supplied callback must accept two parameters, first is the line index (zero based) and second is the line itself (string)
		"""

		if isinstance(handler, DriveClientStreamHandler):
			title, dl_link = self._get_file_metadata(file_id)

			if dl_link:
				handler.stream_process_started(title)
				with requests.get(dl_link, stream=True) as response:
					if response and response.ok:  # basically means HTTP status < 400
						if chunk_size:
							for chunk in response.iter_content(chunk_size=chunk_size):
								if chunk:
									handler.new_chunk_callback(chunk)
						else:
							line_index = 0
							for line in response.iter_lines(chunk_size=chunk_size):
								if line:
									handler.new_line_callback(line_index, line)
									line_index += 1
					else:
						print "Error :: request for stream of lines has failed"
		else:
			print "Error :: invalid handler"

