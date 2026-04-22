import sys
from pathlib import Path

# Make the project root importable so `from cad_view_model import ...` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
