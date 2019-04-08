from threading import Lock

class DLPReporter(object):

	"""
	represents an abstract DLP reporter.
	defines an interface of an entity which receives some new leakage
	data to report about during scan, and just handles the report somehow.
	when working in parallel mode, it is being considered that 'report()' might be invoked
	by more then one scanner simultniesly, so the actual inner '_report_new_data()' method is considered critical
	"""

	def __init__(self, file_title, parallel_mode):
		self.file_title = file_title
		self.lock = Lock() if parallel_mode else None

	def report(self, data_type, data):
		if self.lock is not None:
			self.lock.acquire()
			try:
				self._report_new_data(data_type, data)
			finally:
				self.lock.release()  # release lock, no matter what
		else:
			self._report_new_data(data_type, data)

	def _report_new_data(self, data_type, data):
		raise NotImplementedError("must be implemented in concrete class")

class ConsoleDLPReporter(DLPReporter):

	"""
	reports DLP events to console
	"""

	def __init__(self, file_title, parallel_mode):
		super(ConsoleDLPReporter, self).__init__(file_title, parallel_mode)

	def _report_new_data(self, data_type, data):
		print "Found potential data leakage of type %s in file %s: " % (data_type, self.file_title),
		print data

class FileDLPReporter(DLPReporter):

	"""
	reports DLP events to report file
	"""

	def __init__(self, file_title, parallel_mode):
		super(FileDLPReporter, self).__init__(file_title, parallel_mode)
		self.report_file = open("DLP_Report.txt", "w")
		self.report_file.write("DLP report for %s:\n" % file_title)

	def __del__(self):
		if self.report_file:
			self.report_file.close()

	def _report_new_data(self, data_type, data):
		if self.report_file:
			self.report_file.write("Found potential data leakage of type %s in file %s: " % (data_type, self.file_title))
			self.report_file.write(data + "\n")