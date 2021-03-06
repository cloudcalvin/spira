import os
import gdspy
import numpy as np

# ------------------------------ SPiRA Information -----------------------------

__version__ = '0.0.2'
__release__ = 'Auron'

LIB_NAME = 'SPiRA'
LIB_DESCRIPTION = 'SPiRA: The Virtuoso'
VERSION = 'Version {}-{}'.format(__version__, __release__)
COPYRIGHT_INFO = 'MIT License'
AUTHOR = 'Ruben van Staden'
AUTHOR_EMAIL = 'rubenvanstaden@gmail.com'

START_MESSAGE = '{} - {}'.format(VERSION, COPYRIGHT_INFO)

# ----------------------------- Default Globals --------------------------------

DEG2RAD = np.pi / 180.0
RAD2DEG = 180.0 / np.pi

_current_library = None

DEFAULT_LIBRARY = None

SCALE_UP = 1.0e+6
SCALE_DOWN = 1.0e-6

# ----------------------------- Initialize Library -----------------------------

def initialize():
    from .gdsii.library import Library
    from .rdd.settings import RDD

    global DEFAULT_LIBRARY 
    DEFAULT_LIBRARY = Library('SPiRA-default',
        unit=RDD.GDSII.UNIT,
        precision=RDD.GDSII.PRECISION
    )

    set_library(DEFAULT_LIBRARY)


def set_library(library):
    """ Set the working library. """
    global _current_library
    _current_library = library


def get_library():
    """ Return current working library. """
    if _current_library is None:
        initialize()
    return _current_library

# --------------------------------- Extras -------------------------------------

