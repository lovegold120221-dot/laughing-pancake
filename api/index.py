import sys
import os

# Ensure the root directory is in the path so the 'app' package is discoverable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
