#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Toolbox Lazy Sub-module Loading
:author: Ronan Delacroix
"""
import sys
import importlib


class LazyLoader:
    """
    Module Wrapper Class
    See here for wrapping module class : http://stackoverflow.com/questions/2447353/getattr-on-a-module
    Also does lazy loading of sub modules.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.imports = {}

    def __getattr__(self, name):
        """
        Lazy loading module
        """
        if name.startswith('__'): #importing needs access to some private reserved __*__ functions...
            return getattr(self.wrapped, name)

        if not self.imports.get(name, None):
            self.imports[name] = importlib.import_module('.'+name, package='toolbox')

        return self.imports.get(name, None)


sys.modules[__name__] = LazyLoader(sys.modules[__name__])