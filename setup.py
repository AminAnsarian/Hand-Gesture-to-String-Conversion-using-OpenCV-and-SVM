from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np


extensions = [Extension("calCython", ["calCython.pyx"],
                        language="c++",
						include_dirs=[np.get_include()])]
setup(ext_modules=cythonize(extensions, annotate=True))