from selenium.webdriver.common.by import By


class ByElement(By):
	def __init__(self, by, value):
		self.by = by
		self.value = value

	def __str__(self):
		return '(By.{0}: {1})'.format(self.by, self.value)

	@staticmethod
	def id(value):
		return ByElement(By.ID, value)

	@staticmethod
	def xpath(value):
		return ByElement(By.XPATH, value)

	@staticmethod
	def class_name(value):
		return ByElement(By.CLASS_NAME, value)

	@staticmethod
	def css_selector(value):
		return ByElement(By.CSS_SELECTOR, value)

	@staticmethod
	def link_text(value):
		return ByElement(By.LINK_TEXT, value)

	@staticmethod
	def name(value):
		return ByElement(By.NAME, value)

	@staticmethod
	def partial_link_text(value):
		return ByElement(By.PARTIAL_LINK_TEXT, value)

	@staticmethod
	def tag_name(value):
		return ByElement(By.TAG_NAME, value)
