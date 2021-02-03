# from .GNUProlog import GNUProlog
# from .SWIProlog import SWIProlog
# from .XSBProlog import XSBProlog
# #from .Prolog import Prolog

from pylo.engines.prolog import SWIProlog
from pylo.engines.prolog.prologsolver import Prolog

__all__ = [
    "SWIProlog",
    # "XSBProlog",
    # "GNUProlog",
    "Prolog"
]