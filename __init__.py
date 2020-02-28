import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from parle.func import *
from parle.sym import *
from parle.fun import *
from parle.save import *
from parle.table import *
from parle.files import *
sys.path.pop(0)
