class Singleton:
    _instances = {}
    _initialized = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
            cls._initialized[cls] = False
        return cls._instances[cls]
        
    def __init__(self):
        if not self._initialized.get(self.__class__, False):
            self._init()
            self._initialized[self.__class__] = True
            
    def _init(self):
        """Überschreibe diese Methode in der abgeleiteten Klasse"""
        pass 