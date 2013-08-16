import time

def main(xpng):
    xpng.wait("grub")
    xpng.type("<up>")
    xpng.type("<enter>")
    xpng.wait("language", 40)
    print "System booted."
    xpng.click("continue")
    xpng.wait("nready", 10)
    xpng.wait("ready", 30)
    print "Hub ready."
    xpng.click("storages")
    xpng.wait("disk", 10)
    xpng.click("done")
    xpng.wait("autodisk", 10)
    xpng.click("autodisk")
    xpng.wait("storages_done", 20)
    print "Storage selection done."
    xpng.click("begin")
    xpng.wait("installation", 10)
    print "Installation had started."
    xpng.click("installation")
    xpng.wait("root_pass", 5)
    xpng.type("fedora")
    xpng.type("<tab>")
    xpng.type("fedora")
    xpng.wait("root_typed", 5)
    xpng.type(["<alt>", "d"])
    time.sleep(1)
    xpng.type(["<alt>", "d"])
    xpng.wait("user_installation", 5)
    print "Root account created."
    xpng.click("user_installation")
    xpng.wait("user_create", 10)
    xpng.type("test")
    xpng.type("<space>")
    xpng.type("user")
    xpng.type("<tab>")
    xpng.type("user")
    xpng.type("<tab>")
    time.sleep(1)
    xpng.type("<space>")
    xpng.type("<tab>")
    time.sleep(1)
    xpng.type("<tab>")
    xpng.type("fedora")
    xpng.type("<tab>")
    xpng.type("fedora")
    xpng.wait("user_created", 10)
    xpng.type(["<alt>", "d"])
    time.sleep(1)
    xpng.type(["<alt>", "d"])
    xpng.wait(["user_completed", "user_completed_white"], 10)
    print "User account created."
    xpng.wait("installation_completed", 600)
    print "Installation completed."
    return True