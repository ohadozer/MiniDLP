import re
from schwifty import IBAN

class DLPScannerEventHandler(object):

	"""
	represents an interface for handling scanner events during scan
	"""

	def __init__(self):
		pass

	def new_scan_result_callback(self, pattern_type, data):
		raise NotImplementedError("must be implemented in concrete class")

class DLPScanner(object):

	"""
	represents an abstract DLP scanner.
	the 'scan()' method must be implemented in subclasses and represents
	the behavior of starting a scan operation on some given raw data, all events
	during scan are being raised using the given event handler
	"""

	def __init__(self):
		pass

	def scan(self, data, handler):
		raise NotImplementedError("must be implemented in concrete class")

class DLPSSNScanner(DLPScanner):

	"""
	DLP SSN scanner
	"""

	keywords = ["Social Security", "Social Security#", "Soc Sec", "SSN", "SSNS", "SSN#", "SS", "SSID"]

	def __init__(self):
		super(DLPSSNScanner, self).__init__()

		# the story behind this member comes from some part in the reqiurements doc which was a bit ambiguous:
		# SSN detection method says "9 digits pattern with textual context before or after." but the terms
		# "before" and "after" are a bit unclear, especially the example capture is "My social security number is 123-45-6789"
		# you can see the substring " number is " buffers between the context keyword and the actual SSN data.
		# so to control how long is the maximum buffer between a keyword (before -or- after SSN data) and the data itself
		# set epsilon. zero means keyword anywhere in the doc satisfies the condition
		self.epsilon = 16

	def _containing_keyword(self, data):

		for keyword in DLPSSNScanner.keywords:
			if re.search(keyword, data, re.IGNORECASE):
				return True
		return False

	def _create_regex_fmt(self):

		inner = "\d{9}|\d{3}-\d{2}-\d{4}|\d{3} \d{2} \d{4}"

		if self.epsilon > 0:
			keys = '|'.join(DLPSSNScanner.keywords)
			lim = self.epsilon
			return r'(?:%s)(?:[\s\S]{0,%d})(%s)|(%s)(?:[\s\S]{0,%d})(?:%s)' % (keys, lim, inner, inner, lim, keys)
		else:
			return r'\b%s\b' % inner

	def _parse_single_ssn(self, ssn):
		# when capturing using the epsilon based SSN pattern, we actually get a pair back
		# where one of the pair elements is always populated with the actual SSN data, and the other always empty.
		if isinstance(ssn, tuple):
			return ssn[0]+ssn[1]
		else:
			return ssn

	def scan(self, data, handler):

		if self.epsilon > 0 or self._containing_keyword(data):
			regex_fmt = self._create_regex_fmt()
			ssns = [self._parse_single_ssn(ssn) for ssn in re.findall(regex_fmt, data, re.IGNORECASE)]

			for ssn in ssns:
				handler.new_scan_result_callback("SSN", ssn)

class DLPIBANScanner(DLPScanner):

	"""
	DLP IBAN scanner
	"""

	country_codes = ["AD", "AE", "AL", "AT", "AZ", "BA", "BE", "BG", "BH", "CH", "CR", "CY", "CZ", "DE", "DK", "DO", "EE", "ES", "FI", "FO", "FR", "GB", "GE", "GI", "GL", "GR", "HR", "HU", "IE", "IL", "IS", "IT", "KW", "KZ", "LB", "LI", "LT", "LU", "LV", "MC", "MD", "ME", "MK", "MR", "MT", "MU", "NL", "NO", "PL", "PT", "RO", "RS", "SA", "SE", "SI", "SK", "SM", "TN", "TR", "VG"]

	def __init__(self):
		super(DLPIBANScanner, self).__init__()
		self.regex_fmt = self._create_regex_fmt()

	def _create_regex_fmt(self):
		codes = '|'.join(DLPIBANScanner.country_codes)
		return r'\b(?:%s)\d{2}[ ]?(?:[a-zA-Z\d]{4}[ ]?){1,7}(?:[a-zA-Z\d]{1,3})?\b' % codes

	def _is_checksum_valid(self, iban):
		try:
			_ = IBAN(iban)
			return True
		except:
			return False

	def scan(self, data, handler):

		regex_fmt = self._create_regex_fmt()
		ibans = re.findall(regex_fmt, data)

		for iban in ibans:
			if self._is_checksum_valid(iban):
				handler.new_scan_result_callback("IBAN", iban)
