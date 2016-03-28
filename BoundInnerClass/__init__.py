"""
http://code.activestate.com/recipes/577070-bound-inner-classes/

Copyright (C) 2010-2011 by Alex Martelli and Larry Hastings

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import weakref

class _Worker(object):
	def __init__(self, cls):
		self.cls = cls

	def __get__(self, outer, outer_class):
		if not outer:
			return self.cls
		name = self.cls.__name__
		if name in outer.__dict__:
			return outer.__dict__[name]
		wrapper_bases = [self.cls]
		multiply_inherit = False
		for base in self.cls.__bases__:
			inherit_from = base
			if base.__name__ != name:
				bound_inner_base = getattr(outer, base.__name__, None)
				if bound_inner_base:
					bases = getattr(bound_inner_base, '__bases__', (None,))
					if bases[0] == base:
						inherit_from = bound_inner_base
						multiply_inherit = True
			wrapper_bases.append(inherit_from)
		wrapper = self._wrap(outer, wrapper_bases[0])
		wrapper.__name__ = name
		if multiply_inherit:
			wrapper.__bases__ = tuple(wrapper_bases)
		if getattr(outer.__class__, name, None) == self.cls:
			setattr(outer, name, wrapper)
		return wrapper

class BoundInnerClass(_Worker):
	def _wrap(self, outer, base):
		wrapper_self = self
		assert outer
		outer_weakref = weakref.ref(outer)
		class Wrapper(base):
			def __init__(self, *args, **kwargs):
				wrapper_self.cls.__init__(self, outer_weakref(), *args, **kwargs)
			if wrapper_self.cls.__repr__ is object.__repr__:
				def __repr__(self):
					return ''.join([
						'<',
						self.__module__,
						'.',
						self.__class__.__name__,
						' object bound to ',
						repr(outer_weakref()),
						' at ',
						hex(id(self)),
						'>'])
		return Wrapper

class UnboundInnerClass(_Worker):
	def _wrap(self, outer, base):
		class Wrapper(base):
			pass
		return Wrapper