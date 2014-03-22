class nlist():

	def __init__(self, n, element):
		self.n = n
		self.element = [element]

	def add(self,element):
		if len(self.element) < self.n:
			self.element.append(element)
		else:
			self.element.pop(0)
			self.element.append(element)