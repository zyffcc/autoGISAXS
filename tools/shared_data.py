class SharedData:
    _instance = None  # Protected class variables

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SharedData, cls).__new__(cls, *args, **kwargs)
            cls._instance.init()
        return cls._instance

    def init(self):
        self.data = {}  # Initializing the Shared Data Dictionary
        self.global_modules = {}  # Initializing the Global Modules Dictionary