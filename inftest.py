class InfinityException(Exception):
    pass


class InfinityTestException(Exception):
    pass


class InfinityTest(object):
    def __init__(self, name, log_dir, record, main, vm_name, images):
        self.completed = False
        self.completed_when = None
        self.message = None
        self.name = name
        self.log_dir = log_dir
        self.record = record
        self.main = main
        self.vm_name = vm_name
        self.vm = None
        self.images = images
        self.xpng = None

    def run(self):
        pass