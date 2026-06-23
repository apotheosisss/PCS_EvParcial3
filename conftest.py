"""Permite que pytest importe el paquete nhanes_diabetes desde src/ sin instalacion editable."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
