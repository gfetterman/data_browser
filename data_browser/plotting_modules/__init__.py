import importlib
import os

__all__ = [importlib.import_module('.{}'.format(os.path.splitext(filename)[0]),
                                   __package__)
           for filename
           in os.listdir(os.path.join(os.path.dirname(__file__)))
           if (os.path.splitext(filename)[1] == '.py'
               and not filename.startswith('__'))]

del os, importlib
