from time import sleep
from time import clock
from BoundInnerClass import BoundInnerClass
from datetime import timedelta
from selenium.webdriver.remote.command import Command
from sepy.by_element import ByElement as By
from sepy.driver_element import DriverElement
from sepy import WAIT_MESSAGE_TIME
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSelectorException
from sepy.exceptions import RepeatException


def get_driver(inheritable, location=None, message=None, click_wait=0):
	class Driver(inheritable):
		def __init__(self, msg=None, usr=None, cw=0):
			if location:
				super().__init__(location)
			else:
				super().__init__()
			self.message = msg
			self.user = usr
			self.click_wait = cw

		def find_element(self, by=By.ID, value=None):
			if not By.is_valid(by) or not isinstance(value, str):
				raise InvalidSelectorException('Invalid locator values passed in')
			return self.execute(Command.FIND_ELEMENT, {'using': by, 'value': value}, By(by, value))['value']

		def find_elements(self, by=By.ID, value=None):
			if not By.is_valid(by) or not isinstance(value, str):
				raise InvalidSelectorException('Invalid locator values passed in')
			return self.execute(Command.FIND_ELEMENTS, {'using': by, 'value': value}, By(by, value))['value']

		def create_web_element(self, element_id, by=None):
			return DriverElement(self, element_id, by, self.message, self.click_wait)

		def _unwrap_value(self, value, by=None):
			if isinstance(value, dict) and 'ELEMENT' in value:
				return self.create_web_element(value['ELEMENT'], by)
			elif isinstance(value, list):
				return list(self._unwrap_value(item) for item in value)
			else:
				return value

		def execute(self, driver_command, params=None, by=None):
			if not params:
				params = {'sessionId': self.session_id}
			elif 'sessionId' not in params:
				params['sessionId'] = self.session_id
			params = self._wrap_value(params)
			response = self.command_executor.execute(driver_command, params)
			if response:
				self.error_handler.check_response(response)
				response['value'] = self._unwrap_value(
					response.get('value', None), by)
				return response
			return {'success': 0, 'value': None, 'sessionId': self.session_id}

		def get_element(self, by, waittill=10, idle=.5):
			return self._get(by, self.find_element, waittill, idle)

		def get_elements(self, by, waittill=10, idle=.5):
			return self._get(by, self.find_elements, waittill, idle)

		def _get(self, by, method, waittill=10, idle=.5):
			start = clock()
			element = None
			count = 0
			count_to = int(WAIT_MESSAGE_TIME / idle)
			while clock() - start < waittill:
				try:
					element = method(by.by, by.value)
					start = clock() - waittill
				except NoSuchElementException:
					sleep(idle)
				if count == count_to:
					if self.message:
						self.message.debug('Looking for element \'{0}\' but having trouble finding it. Please Wait...'.format(by))
				count += 1
			if element is None:
				raise NoSuchElementException('Could not find \'{0}\''.format(by))
			return element

		def switch_to_new_window(self):
			current_window = self.current_window_handle
			handles = self.window_handles
			handles.remove(current_window)
			self.switch_to_window(handles.pop())
			return current_window

		@BoundInnerClass
		class Group(object):
			def __init__(self, driver, *args):
				self.bys = list(args)
				self.driver = driver
				self.found_by = None
				self.element = None

			def add(self, by):
				self.bys.append(by)

			def remove(self, by):
				self.bys.remove(by)

			def __str__(self):
				return_string = '['
				for x in range(len(self.bys)):
					return_string = '{0} {1}, '.format(return_string, self.bys[x])
				return '{0}]'.format(return_string[:-2])

			def find(self, waittill=10, idle=.5):
				start = clock()
				self.element = None
				count = 0
				while clock() - start < waittill:
					for by in self.bys:
						try:
							self.element = self.driver.find_element(by=by.by, value=by.value)
							self.found_by = by
							start = clock() - waittill
						except NoSuchElementException:
							sleep(idle)
						if self.element is not None:
							break
					if count == WAIT_MESSAGE_TIME:
						self.driver.message.debug('Looking for a group of elements having trouble finding them. Please Wait...')
					count += 1
				if self.element is None:
					raise NoSuchElementException('Could not find anything in this group {0}'.format(self))

		def make_sure_is_not_checked(self, by, waittill=10, idle=.5):
			elem = self.get_element(by, waittill, idle)
			if elem.is_selected():
				elem.click()

		def make_sure_is_checked(self, by, waittill=10, idle=.5):
			elem = self.get_element(by, waittill, idle)
			if not elem.is_selected():
				elem.click()

		def element_exists(self, by, waittill=10, idle=.5):
			if idle > 0:
				start = clock()
				count = 0
				if waittill:
					while clock() - start < waittill:
						try:
							self.find_element(by=by.by, value=by.value)
							return True
						except NoSuchElementException:
							sleep(idle)
						if count == WAIT_MESSAGE_TIME:
							if self.message:
								self.message.debug(
									'Checking if element \'{0}\' exists but having trouble finding it. Please Wait...'.format(by)
								)
							count = 0
						count += 1
				else:
					try:
						self.find_element(by=by.by, value=by.value)
						return True
					except NoSuchElementException:
						pass
				return False
			else:
				raise ValueError('"idle" time cannot be equal to or less than zero.')

		def element_visible(self, by, waittill=10, idle=.5):
			if idle > 0:
				start = clock()
				count = 0
				count_to = int(WAIT_MESSAGE_TIME / idle)
				if waittill:
					while clock() - start < waittill:
						try:
							visible = self.find_element(by=by.by, value=by.value).is_displayed()
							if not visible:
								sleep(idle)
							else:
								return visible
						except NoSuchElementException:
							sleep(idle)
						if count == count_to:
							if self.message:
								self.message.debug(
									'Checking if element \'{0}\' is visible but having trouble seeing it. Please Wait...'.format(by)
								)
							count = 0
						count += 1
				else:
					try:
						return self.find_element(by=by.by, value=by.value).is_displayed()
					except NoSuchElementException:
						pass
				return False
			else:
				raise ValueError('"idle" time cannot be equal to or less than zero.')

		def repeat(self, times=5, wait=5):
			def wrap(f):
				def wrapped(*args):
					count = 0
					start = clock()
					while count < times:
						try:
							f(*args)
							count = times + 1
						except NoSuchElementException as e:
							count += 1
							sleep(wait)
							if clock() - start > WAIT_MESSAGE_TIME:
								if self.message is not None:
									self.message.debug('{0}. Trying again, please wait.'.format(e.msg))
					if count == times:
						if self.message is not None:
							self.message.warn('Couldn\'t execute {0}'.format(f.__name__))
						raise RepeatException(f.__name__)
				return wrapped()
			return wrap

		def try_loop(self, loop_info=''):
			def wrap(f):
				def wrapped(*args):
					try:
						f(*args)
					except (NoSuchElementException, RepeatException) as e:
						if self.message is not None:
							self.message.error('Red:{0}. Skipping the rest of {1}.'.format(e.msg, loop_info))
					except Exception as e:
						if self.message is not None:
							self.message.error('Red:{0} Skipping the rest of {1}.'.format(e, loop_info))
				return wrapped()
			return wrap

		def execute_driver(self):
			def wrap(f):
				def wrapped(*args):
					try:
						start = clock()
						self.message.info('Starting process...')
						f(*args)
						self.message.info('Complete {0}'.format(timedelta(seconds=int(clock() - start))))
					except (NoSuchElementException, RepeatException) as e:
						if self.message is not None:
							self.message.error('End:{0}. Terminating process.'.format(e.msg))
						raise
					except Exception as e:
						if self.message is not None:
							self.message.error('End:{0}. Terminating process.'.format(e))
						raise
					finally:
						self.quit()
						self.message.reset()
				return wrapped()
			return wrap
	return Driver(message, click_wait)
