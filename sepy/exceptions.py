from selenium.common.exceptions import WebDriverException


class RepeatException(WebDriverException):
	def __init__(self, f):
		self.f = f
		self.msg = '{0} was repeated but failed to execute successfully'.format(self.f)

	def __str__(self):
		return '{0} was repeated but failed to execute successfully'.format(self.f)
