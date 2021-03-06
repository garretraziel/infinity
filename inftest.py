import os
import datetime
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
        self.verbose = False
        self.ok = None

    def run(self):
        result = self.main(self.xpng)

        if isinstance(result, tuple):
            self.ok, self.message = result
        elif result is None:
            self.ok = True  # I guess...
            self.message = "[NONE]"
        else:
            self.ok = result
            self.message = str(result)

        self.completed = True
        self.completed_when = datetime.datetime.now()
        return self.ok, self.message

    def build_vm(self):
        created = False
        #TODO: do this, but with better and cleaner code. Move it into build()?
        while not created:
            self.vm = base.build(self.vm_xml, self.storage_xml, self.live_medium)

            if not self.vm:  # there was problem with creating VM. Domain with that ID probably exists
                # if self.verbose:
                #     stdout_handler = sys.stdout
                #     sys.stdout = inflogging.ORIG_STDOUT
                #     clean = raw_input("[ERROR]: Domain already running. Clean it? [Y/n]: ")
                #     if clean not in ["", "Y", "y"]:
                #         base.ID += 1  # TODO: clean existing&running domains instead
                #     else:
                #         base.ID += 1
                #     sys.stdout = stdout_handler
                # else:
                #     # Don't delete existing domains, they might be important. Increase ID instead.
                #     base.ID += 1
                base.ID += 1
            else:
                created = True

        self.xpng = Xpresserng(self.vm.ip, self.vm.port)

        if self.verbose:
            print "Connect to VNC using: vncviewer -shared -viewonly", self.vm.vnc_info()

        self.xpng.load_images(self.images)
        inflogging.create_test_logs(self.name)
        if self.record:
            self.xpng.set_recording(os.path.join(inflogging.CURRENT_LOGDIR, inflogging.nameify(self.name) + ".avi"))

    def tear_down(self):
        base.tear_down(self.vm)
        #TODO: ...

    def set_verbose(self):
        self.verbose = True