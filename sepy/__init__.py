WAIT_MESSAGE_TIME = 4


class Message(object):
	def __init__(self, logger=None):
		if logger:
			self.logger = logger
		else:
			import logging
			self.logger = logging.getLogger('messageDummy')
		self.message = []
		self.errors = ''

	def _append_message(self, new_message):
		self.message.append(str(new_message))

	@staticmethod
	def _clean_message(new_message):
		return new_message.replace('End:', '').replace('Red:', '').replace('Green:', '')

	def send(self, new_message, error=False):
		if error:
			self.errors += self._clean_message(new_message) + '\r\n'
		self._append_message(new_message)

	def debug(self, new_message):
		self._append_message(new_message)
		self.logger.debug(self._clean_message(new_message))

	def info(self, new_message):
		self._append_message(new_message)
		self.logger.info(self._clean_message(new_message))

	def warn(self, new_message):
		self._append_message(new_message)
		self.logger.warn(self._clean_message(new_message))

	def warning(self, new_message):
		self._append_message(new_message)
		self.logger.warn(self._clean_message(new_message))

	def harsh_warning(self, new_message):
		self._append_message(new_message)
		self.errors += self._clean_message(new_message) + '\r\n'
		self.logger.warn(self._clean_message(new_message))

	def error(self, new_message):
		self._append_message(new_message)
		self.errors += self._clean_message(new_message) + '\r\n'
		self.logger.error(self._clean_message(new_message))

	def critical(self, new_message):
		self._append_message(new_message)
		self.errors += self._clean_message(new_message) + '\r\n'
		self.logger.critical(self._clean_message(new_message))

	def reset(self):
		self.message = []
		self.errors = ''
