class nlist():

	def __init__(self, n, element):
		self.n = n
		self.element = [element]

	def add(self,element):
		if len(self.element) < self.n:
			self.element.insert(0,element)
		else:
			self.element.pop()
			self.element.insert(0,element)