# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2007 Marco Antonio Islas Cruz
#
# Christine is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Christine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @category  libchristine
# @package   Validator
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @author    Rodrigo Garcia <nibblesmx@gmail.com>
# @copyright 2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import os

#
# Compare if it is none or not
#
# @param  void
# @return boolean
def isNull(value):
	"""
	Compare if it is none or not
	"""
	if (value is not None):
		return False
	
	return True

#
# Compare if it is none or not
#
# @param  void
# @return boolean
def isBoolean(value = None):
	"""
	Compare if it is boolean or not
	"""
	return (type(value) == bool)

#
# Compare if it is integer or not
#
# @param  void
# @return boolean
def isInteger(value = None):
	"""
	Compare if it is integer or not
	"""
	return (type(value) == int)

#
# Compare if it is float or not
#
# @param  void
# @return boolean
def isFloat(value = None):
	"""
	Compare if it is float or not
	"""
	return (type(value) == float)

#
# Compare if it is string or not
#
# @param  void
# @return boolean
def isString(value = None):
	"""
	Compare if it is string or not
	"""
	return (type(value) == str)

#
# Compare string if it is empty or not
#
# @param  void
# @return boolean
def isStringEmpty(value = None):
	"""
	Compare string if it is empty or not
	"""
	return (len(value) == 0)

#
# Compare if it is a file or not
#
# @param  void
# @return boolean
def isFile(value = None):
	"""
	Compare if it is a file or not
	"""
	return os.path.isfile(value)