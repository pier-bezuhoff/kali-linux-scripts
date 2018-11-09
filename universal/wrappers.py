# -*- coding: utf-8 -*-
# python3 compatible
# ♑

from time import time, asctime
import random

# remember of timeit.timeit()

def standard(func, arg_list, arg_dict, return_answer=True, print_output=True):
	output = ''
	start_time = time()
	result = func(*arg_list, **arg_dict)
	end_time = time() - start_time
	output += "Wrapping function 'standard'.\nWrapped function \'{}\'.\nResult: {}.\nEstimated time: {}s\n(current time: {}).".format(func.__name__, result, end_time, asctime())
	if return_answer:
		output += '\n' + str(result)
	if print_output:
		print(output)
	else:
		return output

def repeater(func, arg_list=None, min=0, max=100, number=100, return_answer=False, print_output=True):
	output = ''
	if not arg_list:
		arg_list = [random.randint(min, max) for _ in range(number)]
	n = 0
	l = len(arg_list)
	result_list = []
	start_time = time()
	for arg in arg_list:
		result_list.append(func(arg))
	end_time = time() - start_time
	output += "Wrapping function 'repeater'.\nWrapped function \'{}\'.\nEstimated time: {}s\naverage time: {}\n(current time: {}).\n".format(func.__name__, end_time, end_time/len(arg_list), asctime())
	output += "Sum: {}, number: {}, average: {}.".format(sum(result_list), l, 1.0*sum(result_list)/l)
	if return_answer:
		output += '\n' + str(result_list)
	if print_output:
		print(output)
	else:
		return output

def comparator(func1, func2, arg_list=None, min=0, max=100, number=100, check_equal=False, print_output=True):
	output = ''
	output += "Wrapping function 'comparator'.\n"
	if not arg_list:
		arg_list = [random.randint(min, max) for _ in range(number)]
	start_time = time()
	for arg in arg_list:
		func1(arg)
	end_time = time() - start_time
	output += "Wrapped function \'{}\'; estimated time: {}s, average time: {}s.\n".format(func1.__name__, end_time, end_time/len(arg_list))
	start_time = time()
	for arg in arg_list:
		func2(arg)
	end_time = time() - start_time
	output += "Wrapped function \'{}\'; estimated time: {}s, average time: {}s\n(current time: {}).".format(func2.__name__, end_time, end_time/len(arg_list), asctime())
	if check_equal:
		for arg in arg_list:
			if func1(arg) != func2(arg):
				output += "\nNot always equal. For example at {}.".format(arg)
				break
		else:
			output += "\nEqual on the arg list."
	if print_output:
		print(output)
	else:
		return output
