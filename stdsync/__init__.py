# ==================== stdsync/__init__.py ===================
"""
StdSync 包初始化模块
"""
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("stdsync")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "__version__",
]