"""Scour registry. To add a new scour: subclass Scour in a new module under
this package, then register the class in REGISTRY below."""
from .prometheus_self import PrometheusSelfScour

REGISTRY = [
    PrometheusSelfScour,
]
