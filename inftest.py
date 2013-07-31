import os
from v12n import base
from xpresserng import Xpresserng
import inflogging


class InfinityTest(object):
    def __init__(self, name, record, main, vm_xml, storage_xml, live_medium, images):
        self.completed = False
        self.completed_when = None
        self.message = None
        self.name = name
        self.record = record
        self.main = main
        self.vm_xml = vm_xml
        self.storage_xml = storage_xml
        self.vm = None
        self.images = images
        self.xpng = None
        self.live_medium = live_medium

    def run(self):
        self.message = self.main(self.xpng, inflogging.log)
        self.completed = True

    def build_vm(self):
        self.vm = base.build(self.vm_xml, self.storage_xml, self.live_medium)
        self.xpng = Xpresserng(self.vm.ip, self.vm.port)
        self.xpng.load_images(self.images)
        inflogging.create_test_logs(self.name)
        if self.record:
            self.xpng.set_recording(
                os.path.join(inflogging.CURRENT_LOGDIR, self.name.lower().replace(" ", "_") + ".webm"))

    def tear_down(self):
        base.tear_down(self.vm)
        #TODO: ...