# -*- coding: utf-8 -*-
#!usr/bin/env python3

import re
import itertools

def scale_of_notation(number, from_scale, to_scale=10):
	"""translate the number from one scale of notation into another.
	scale_of_notation(str, int, int) --> str
	scale_of_notation(int, int, int) --> str"""
	sign = '+'
	number = str(number)
	if number.startswith('-'):
		number = number[1:]
		sign = '-'
	if from_scale != 10:
		# to decimal
		s = 0
		for i in range(len(number)):
			digit = number[i]
			if not digit in [str(x) for x in range(0, 10)]:
				digit = ord(digit) - ord('A') + 10
			else:
				digit = int(digit)
			assert(digit < from_scale)
			s += digit*(from_scale**(len(number) - 1 - i))
		number = str(s)
	if to_scale == 10:
		if sign == '-':
			number = '-' + number
		return number
	# from decimal
	number = int(number)
	result = []
	while number != 0:
		result.append(str(number%to_scale))
		number//=to_scale
	result.reverse()
	for i in range(len(result)):
		if len(result[i]) > 1:
			result[i] = chr(ord('A') + int(result[i]) - 10)
	number = ''.join(result)
	if sign == '-':
		number = '-' + number
	return number

def scale_eval(string, sep='_', verbose=False):
	"""eval the string replacing <int>_<int> numbers with decimal <int>
	sep must be used only for scale of notation
	example: scale_eval("D_16 + 366_7") == 208
	scale_eval(str) --> evaluated type"""
	a_number = "[ABCDEFGHIJKLMNOPQRSTUVWXYZ\d]*" # or [''.join([chr(i) for i in range(ord('A'), ord('Z') + 1)])+'\d']*,
	# or \w*, or [^\@\%\^\&\*\**\/\//\-\ + \=\~\(\)\[\]\{\}\'\"\:\;\,\.\<\>\?\!\$\#\№\`\|]*
	a_notation = "\d*"
	pattern = re.compile(a_number + sep + a_notation)
	while sep in string:
		x = pattern.search(string).group()
		y = x.split(sep)
		number = y[0]
		scale = int(y[1])
		string = re.sub(x, scale_of_notation(number, scale, 10), string)
	if verbose:
		print(string)
	return eval(string)

def input_scale_eval():
	"""= scale_eval(input())"""
	return scale_eval(input())

def extended_count(list_, first=0, separator=''):
	"""a-la count generator,
	extended_count(iterable, int, str) --> generator
	example: extended_count("AbCde$", 2, '-') -->
	'C' 'd' 'e' '$' 'A-A' 'A-b' 'A-C' 'A-d' 'A-e' 'A-$' 'b-A' ..."""
	list_ = [str(x) for x in list_]
	if len(set(list_)) != len(list_):
		raise IndexError("Some element in 'list_' repeated 2 or more times")
	if type(list_) is not tuple:
		list_ = tuple(list_)
	x = [list_[first], ]
	last_element = list_[-1]
	first_element = list_[0]
	while True:
		yield separator.join(x)
		if x[-1] != last_element:
			x[-1] = list_[list_.index(x[-1]) + 1]
		else:
			mi = -1
			to_next = True
			while to_next and mi >= -len(x):
				if x[mi] == last_element:
					x[mi] = first_element
					if mi == -len(x):
						x = [first_element, ] + x
						to_next = False
				else:
					x[mi] = list_[list_.index(x[mi]) + 1]
					to_next = False
				mi -= 1

def extended_countlist(list_, length, first=0, separator=''):
	"""a-la count list,
	extended_countlist(iterable, int, int, str) --> generator
	example: extended_count("AbCde$", 11, 2, '-') -->
	['C', 'd', 'e', '$', 'A-A', 'A-b', 'A-C', 'A-d', 'A-e', 'A-$', 'b-A']"""
	count = extended_count(list_, first, separator)
	l = list()
	for _ in range(length):
		l.append(next(count))
	return l

eng_keyboard = 'qwertyuiop[]asdfghjkl;\'zxcvbnm,./`'
rus_keyboard = 'йцукенгшщзхъфывапролджэячсмитьбю.ё'
deqoder_dict1 = dict(zip(eng_keyboard, rus_keyboard))
deqoder_dict2 = {deqoder_dict1[k]: k for k in deqoder_dict1}

def deqoder(text, lang=None):
	"""simulate keyboard layouts
	dequader(str, <to 'rus', 'eng' or None (= autodetection)>)
	example: deqoder("j,jhjntym", 'rus') --> "оборотень"
	asdf... <--> фыва..."""
	if lang is None:
		if sum(text.count(ch) for ch in eng_keyboard) >= sum(text.count(ch) for ch in rus_keyboard):
			lang = 'rus'
		else:
			lang = 'eng'
	if lang == 'eng':
		for i in range(len(text)):
			if text[i] in deqoder_dict2.keys():
				text = text[:i] + deqoder_dict2[text[i]] + text[i + 1:]
	elif lang == 'rus':
		for i in range(len(text)):
			if text[i] in deqoder_dict1.keys():
				text = text[:i] + deqoder_dict1[text[i]] + text[i + 1:]
	return text

