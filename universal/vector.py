# -*- coding: utf-8 -*-
# python2(?) and python3 compatible # ? -- excluding setters and some functions
# ♑

import math
import random
from copy import copy

class Vector():
	"""Cutomized magic vector class."""

	ORT_X = (1, 0) # right
	ORT_Y = (0, 1) # down

	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)

	def __add__(self, other):
		"Return sum ('+') of the two vectors."
		return Vector(self.x + other.x, self.y + other.y)

	def __and__(self, other):
		"Return abs() of vector product ('&') of the two vectors."
		return (self.x*other.y - self.y*other.x)

	def __div__(self, number):
		"Return this vector divided ('/') by the number. Python2."
		return Vector(self.x*1.0 / number, self.y*1.0 / number)

	def __eq__(self, other):
		"If equals ('==')."
		return (self.x == other.x) and (self.y == other.y)

	def __ge__(self, other):
		"Compare lengths using '>='."
		return self.length >= other.length

	def __getitem__(self, key):
		if key in (0, 'x'):
			return self.x
		elif key in (1, 'y'):
			return self.y

	def __gt__(self, other):
		"Compare lengths using '>'."
		return self.length > other.length

	def __iadd__(self, other):
		"Add other vector using '+='."
		self.x += other.x
		self.y += other.y
		return self

	def __idiv__(self, number):
		"Divide by number using '/='. Python2/"
		self.x *= 1 / number
		self.y *= 1 / number
		return self

	def __imod__(self, matrix):
		"Multiply ('%=') every coordinate by matrix index"
		self.x *= matrix[0]
		self.y *= matrix[1]
		return self

	def __imul__(self, number):
		"Multiply by number using '*='."
		self.x *= number
		self.y *= number
		return self

	def __invert__(self):
		"Invert using '~'."
		self.x = -self.x
		self.y = -self.y
		return self

	def __isub__(self, other):
		"Subtract other vector using '-='."
		self.x -= other.x
		self.y -= other.y
		return self

	def __iter__(self):
		return iter((self.x, self.y))

	def __itruediv__(self, number):
		"Divide by number using '/='. Python3."
		self.x *= 1 / number
		self.y *= 1 / number
		return self

	def __ixor__(self, theta):
		"Set specified angle ('^=') to this vector."
		x = self.length*math.cos(theta)
		y = math.sqrt(abs(self.qlength - x*x))
		# if self.qlength - x*x < 0:
		#	print('Suspected equation in Vector.__ixor__')
		if theta > 0:
			y = -y
		self.x = x
		self.y = y
		return self

	def __le__(self, other):
		"Compare lengths using '<='."
		return self.length <= other.length

	def __lshift__(self, length = 1):
		"Return left normal ('<<') with specified length (deault: 1)."
		return (Vector(-self.y, self.x) | length)

	def __lt__(self, other):
		"Compare lengths using '<'."
		return self.length < other.length

	def __mod__(self, matrix):
		"Return vector of the vector coordinates multiplied ('%') by matrix indexes."
		return Vector(self.x*matrix[0], self.y*matrix[1])

	def __mul__(self, number):
		"Return this vector multiplied ('*') by the number."
		return Vector(number*self.x, number*self.y)

	def __ne__(self, other):
		"If not equals ('!=')."
		return (self.x != other.x) or (self.y != other.y)

	def __neg__(self):
		"Return inverted instance using '-'."
		return Vector(-self.x, -self.y)

	def __or__(self, length=1):
		"Scale to specified length using '|'."
		l = self.length
		if l != 0:
			self.x *= (length / l)
			self.y *= (length / l)
		else:
			self.x = length
		return self

	def __pow__(self, other):
		"Return scalar product ('**') of the two vectors."
		return (self.x*other.x + self.y*other.y)

	def __repr__(self):
		return 'Vector ({0}, {1})'.format(self.x, self.y)

	def __rmul__(self, number):
		"Return this vector multiplied ('*') by the number."
		return Vector(number*self.x, number*self.y)

	def __round__(self):
		return Vector(round(self.x), round(self.y))

	def __rshift__(self, length = 1):
		"Return right normal ('>>') with specified length (default: 1)."
		return (Vector(self.y, -self.x) | length)

	def __setitem__(self, key, value):
		if key in (0, 'x'):
			self.x = value
		elif key in (1, 'y'):
			self.y = value

	def __str__(self):
		return '2D vector with x = {0}, y = {1},\n length = {2} and angle = {3}*Pi.'\
				.format(self.x, self.y, self.length, self.angle / math.pi)

	def __sub__(self, other):
		"Return difference ('-') between the two vectors."
		return Vector(self.x - other.x, self.y - other.y)

	def __truediv__(self, number):
		"Return this vector divided ('/') by the number. Python3."
		return Vector(self.x*1.0 / number, self.y*1.0 / number)

	def __xor__(self, other):
		"Return angle in radians('^') from the first vector to the second vector."
		return (self.angle - other.angle)

	def decreased(self, number):
		"Return the vector with length decreased by the number."
		return copy(self).with_length(self.length - number)

	def distance(self, other):
		return math.hypot(self.x-other.x, self.y-other.y)
	
	def get_int_tuple(self):
		return (int(self.x), int(self.y))

	def get_line(self, point):
		"Return 3 line equation coefficients. Line: a*x + b*y + c = 0 (a*a + b*b = 1)"
		x1, y1 = point
		x2, y2 = self + Vector(*point)
		a = y2 - y1
		b = x1 - x2
		c = x2*y1 - x1*y2
		l = math.hypot(a, b)
		a /= l
		b /= l
		c /= l
		return a, b, c

	def get_normal(self, length=1):
		"Negative length means left normal."
		if length > 0:
			return self >> length
		else:
			return self << length

	def increased(self, number):
		"Return the vector with length increased by the number."
		return copy(self).with_length(self.length + number)

	def reflected(self, other):
		"Return the vector reflected relatively to the other vector."
		return self.rotated(-2*(self ^ other))

	def rotate(self, angle):
		"Rotate by the angle."
		self ^= self.angle + angle
		return self

	def rotated(self, angle):
		"Return the vector rotated by the angle."
		return copy(self).rotate(angle)

	def with_angle(self, angle):
		vector = copy(self)
		vector ^= angle
		return vector

	def with_length(self, length):
		vector = copy(self)
		vector | length
		return vector

	def zero(self):
		self = Vector(0, 0)
		return self

	@property
	def angle(self):
		"Angle measured anticlockwise."
		if self.length == 0:
			angle = 0.0 # the next algorithm find the string
		# with open('vector.py', 'r') as the_file:
		# 	the_code = the_file.readlines()
		# res_line = 0
		# for line in the_code:
		# 	if 'angle = 0.0 # the next algorithm find the string' in line:
		# 		res_line = the_code.index(line)
		# print('Found angle of 0-vector!')
		# print('File {},\
		# 			line {}, in angle:'.format(__file__, res_line - 4)) # - 4 is a crutch
		# print(' '*4 + '@property\n' + ' '*4 + 'def angle(self): ...')
		else:
			angle = math.acos(self ** Vector(*Vector.ORT_X)/self.length)
			if self.y > 0:
				angle = -angle
		return angle

	@angle.setter
	def angle(self, new_angle):
		x = self.length*math.cos(new_angle)
		y = math.sqrt(abs(self.qlength - x*x))
		if ( self.qlength - x*x < 0 ):
			print('Suspected equation in Vector.angle.setter')
		if theta > 0:
			y = -y
		self.x = x
		self.y = y
		return self

	@property
	def length(self):
		return math.hypot(self.x, self.y)

	@length.setter
	def length(self, new_length):
		assert (new_length >= 0), "length must be positive or zero"
		l = self.length
		if l != 0:
			self.x *= (new_length / l)
			self.y *= (new_length / l)
		else:
			self.x = new_length # self = (Vector(*ORT_X)*length); hm...
		return self

	@property
	def qlength(self):
		"Squared length."
		return (self.x*self.x + self.y*self.y)

	@qlength.setter
	def qlength(self, new_qlength):
		assert (new_qlength >= 0), "qlength must be positive or zero"
		ql = self.qlength
		if ql != 0:
			self.x *= math.sqrt(new_qlength / ql)
			self.y *= math.sqrt(new_qlength / ql)
		else:
			self.x = math.sqrt(new_qlength) # self = (Vector(*ORT_X)*length); hm...
		return self




def Polar(length, angle):
	"Create polar-specified vector."
	return Vector(length*math.cos(angle), -length*math.sin(angle))

def Random(a=10, b=10):
	return Vector(a*(2*random.random() - 1), b*(2*random.random() - 1))

def Zero():
	return Vector(0, 0)

def distance(vector1, vector2):
		return math.hypot(vector1.x-vector2.x, vector1.y-vector2.y)

def vector_sum(*vectors):
	if len(vectors) == 0:
		return Vector(0, 0)
	else:
		return Vector(sum([v.x for v in vectors]), sum([v.y for v in vectors]))