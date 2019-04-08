from DLPScanner import *
from DLPReporter import *
from DriveClient import *
import threading

class DLPEngine(DLPScannerEventHandler, DriveClientStreamHandler):

	"""
	represents a (Mini)DLP engine.
	exposes a go method, to just be supplied with a file ID in Google Drive.
	creates it's internal scanners and reporters and starts working
	must be supplied with a valid (authenticated) Drive client during construction.
	can work either in parallel scan mode, or not.
	"""

	def __init__(self, drive_client, parallel_mode=True):
		super(DLPEngine, self).__init__()
		self.drive_client = drive_client
		self.reporters = None
		self.parallel_mode = parallel_mode
		self.scanner_threads = []

	def _create_reporters(self, file_title):
		return [ConsoleDLPReporter(file_title, self.parallel_mode), FileDLPReporter(file_title, self.parallel_mode)]

	def _create_scanners(self):
		return [DLPSSNScanner(), DLPIBANScanner()]

	def _start_scanner(self, scanner, file_data):
		try:
			scanner.scan(file_data, self)
		except Exception as ex:
			print "Error :: unhandled error in scanner: %s" % str(ex)

	def _handle_data_to_scan(self, data):

		scanners = self._create_scanners()

		# iterate all leakage scanners
		# start actual scanning in each of them
		for scanner in scanners:
			if self.parallel_mode:
				t = threading.Thread(target=self._start_scanner, args=(scanner, data))
				self.scanner_threads.append(t)
				t.start()
			else:
				self._start_scanner(scanner, data)

	def new_scan_result_callback(self, pattern_type, data):

		# iterate reporters, let each of them do its report
		for reporter in self.reporters:
			reporter.report(pattern_type, data)

	def new_line_callback(self, line_index, line):
		raise NotImplementedError("must be implemented in concrete class")

	def new_chunk_callback(self, buffer):
		raise NotImplementedError("must be implemented in concrete class")

	def stream_process_started(self, file_title):
		raise NotImplementedError("must be implemented in concrete class")

	def go(self, file_id, chunk_size=0):

		if chunk_size:
			stream = self.drive_client.get_stream(file_id, chunk_size=chunk_size)
			file_title, file_data = next(stream)
		else:
			file_title, file_data = self.drive_client.get_content(file_id)

		if file_title and file_data:

			print "\nStarting analysis for %s" % file_title

			self.reporters = self._create_reporters(file_title)

			self._handle_data_to_scan(file_data)

			if chunk_size:
				for _, file_data in stream:
					self._handle_data_to_scan(file_data)

			for t in self.scanner_threads:
				t.join()

			print "Finished analysis for %s" % file_title
