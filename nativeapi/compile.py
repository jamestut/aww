#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(
	name = "nativeapi",
	version = "1.0",
	ext_modules = [Extension("nativeapi", ["module.c"])],
	);
