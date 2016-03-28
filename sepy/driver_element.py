import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.command import Command
from sepy import WAIT_MESSAGE_TIME


class DriverElement(WebElement):
	def __init__(self, parent, id_, by, message=None, click_wait=0):
		super().__init__(parent, id_)
		self.by = by
		self.click_tries = 0
		self.message = message
		self.click_wait = click_wait

	def click(self, delay=0):
		self.click_tries += 1
		if delay:
			time.sleep(delay)
		self._execute(Command.CLICK_ELEMENT)
		time.sleep(self.click_wait)

	def get_element(self, by, waittill=10, idle=.5):
			return self._get(by, self.find_element, waittill, idle)

	def get_elements(self, by, waittill=10, idle=.5):
		return self._get(by, self.find_elements, waittill, idle)

	def _get(self, by, method, waittill=10, idle=.5):
		start = time.clock()
		element = None
		count = 0
		count_to = int(WAIT_MESSAGE_TIME / idle)
		while time.clock() - start < waittill:
			try:
				element = method(by.by, by.value)
				start = time.clock() - waittill
			except NoSuchElementException:
				time.sleep(idle)
			if count == count_to:
				if self.message:
					self.message.debug(
						'Looking for element \'{0}\' by {1} but having trouble finding it. Please Wait...'.format(by.value, by.by)
					)
			count += 1
		if element is None:
			raise NoSuchElementException('Could not find \'{0}\' by {1}'.format(by.value, by.by))
		return element

	def __str__(self):
		return '{0}'.format(self.by)
