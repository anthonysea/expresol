from .Data import *

class Parser:	
	def __init__(self, types=[]):
		self.vocab = {}
		self.rules = []
		for i in range(len(types)):
			self.vocab[types[i]] = None
	
	def __call__(self, script, memory):
		data = self.parse(script)
		model = self.convert(data, memory)
		return self.execute(model)

	def rule(self, type1, type2):
		self.rules.append((type1, type2))
	
	def type(self, name, chars):
		self.vocab[name] = chars
		
	def parse(self, script):
		labels = []
		types = list(self.vocab.keys())
		script = combine(revise(script))
		for i in range(len(types)):
			labels.append(assign_labels(script, self.vocab[types[i]], types[i]))
		objects = combine_elements(script, merge(labels), self.rules)
		return objects
	
	def convert(self, objects, memory):
		data = convert_objects(objects, memory)
		boundaries =define_boundaries(data)
		containers = assign_containers(boundaries)
		model = generate(boundaries, containers, data)
		return model

	def execute(self, model):
		for i in range(len(model)):
			if isinstance(model, list):
				function = None
				inputs = list()

				if len(model) == 1:
					function = ID
					inputs = [model[0]]
				elif len(model) == 2:
					function = model[0]
					inputs = [model[1]]
				elif len(model) == 3:
					function = model[1]
					inputs = [model[0], model[2]]

				operator = Operator(function)
				for j in range(len(inputs)):
					if isinstance(inputs[j], list):
						inputs[j] = self.execute(inputs[j])
				return operator(inputs)

def contains(r1, r2):
	i1, f1 = r1
	i2, f2 = r2
	return i1 < i2 and f1 > f2

def combine(strings):
	string = ''
	for i in range(len(strings)):
		string += strings[i]
	return string

def revise(statement):
	strings = []
	string = ''
	statement += ' '
	for i in range(len(statement)):
		char = statement[i]

		if char == ' ':
			if len(string) > 0:
				strings.append(string)
				string = ''
		else:
			string += char
	return strings

def merge(sets):
	outputs = []
	for i in range(len(sets[0])):
		labels = []
		for j in range(len(sets)):
			label = sets[j][i]
			if label != None:
				labels.append(label)
		output = None
		if len(labels) > 0:
			output = labels[0]
		outputs.append(output)
	return outputs

def assign_labels(statement, symbols, label):
	markers = []
	for i in range(len(statement)):
		marker = None
		char = statement[i]
		if char in symbols:
			marker = label
		markers.append(marker)
	return markers

def combine_elements(statement, markers, rules):
	pc = ''
	pm = 'none'
	string = ''
	labels = []
	strings = []
	for i in range(len(statement)):
		m = markers[i]		
		c = statement[i]
		if (pm, m) in rules:
			string += c
		elif len(string) > 0:
			strings.append(string)
			labels.append(pm)
			string = c
		pc = c
		pm = m
	return strings

def convert_objects(objects, memory):
	elements = []
	for i in range(len(objects)):
		symbol = objects[i]
		elements.append(memory.get(symbol))
	return elements

def define_boundaries(elements):
	indices = []
	markers = []
	boundaries = []
	for i in range(len(elements)):
		data = elements[i]['value']
		if isinstance(data, Marker) and data['label'] != 'end':
			if data['label'] == 'open':
				indices.append(i)
				markers.append(data['label'])
		
			elif data['label'] == 'close':
				pm = markers[len(markers)-1]
				if pm == 'open':
					pi = indices[len(indices)-1]
					boundaries.append((pi, i))
					del indices[len(indices)-1]
					del markers[len(markers)-1]	
		else:
			boundaries.append((i, i))
	return boundaries

def assign_containers(boundaries):
	containers = []
	for i in range(len(boundaries)):
		containers.append([])
		for j in range(len(boundaries)):
			range1 = boundaries[i]
			range2 = boundaries[j]
			if contains(range1, range2):
				containers[i].append((j))

	for i in range(len(containers)):
		indices = containers[i]
		for j in range(len(indices)):
			for k in range(len(indices)):
				child = indices[j]
				if indices[k] in containers[child]:
					indices[k] = None
		containers[i] = indices
	
	for i in range(len(containers)):
		indices = []
		for j in range(len(containers[i])):
			if containers[i][j] != None:
				indices.append(containers[i][j])
		containers[i] = indices
	return containers

def generate(boundaries, containers, objects, index=None):
	if index == None:
		index = len(containers)-1
	if len(containers[index]) != 0:
		outputs = []	
		for i in range(len(containers[index])):
			child = containers[index][i]
			outputs.append(generate(boundaries, containers, objects, child))
		return outputs	
	else:
		i,f = boundaries[index]
		if i == f:
			return objects[i]['value']
		else:
			for j in range(i, f):
				if isinstance(objects[j], Marker) == False:
					outputs.append(objects[j]['value'])