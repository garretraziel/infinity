# (c) Jan Sedlak, Red Hat
"""Base functions for creating virtual machines.

This module includes VirtualMachine class for preserving
virtual machines and functions for creating VirtualMachine
objects, creating virtual pools and virtual volumes and
destroying them.

"""

import os
import libvirt
import inflogging
from xml.dom.minidom import parseString

LIBVIRT_CONNECTION = None
MANAGED_VM_DOMAINS = []


def setup_v12n(uri, pool_path):
    global LIBVIRT_CONNECTION

    # connect to libvirt
    if not LIBVIRT_CONNECTION:
        LIBVIRT_CONNECTION = libvirt.open(uri)  # needs root access

    # create pool for storages
    xml_file = open("xml/pool.xml")
    xml_pool = xml_file.read()
    xml_pool = xml_pool.format(path=pool_path)
    if not os.path.exists(pool_path):
        os.mkdir(pool_path)
    xml_dom = parseString(xml_pool)
    xml_pool_name = xml_dom.getElementsByTagName("name")
    if len(xml_pool_name) != 1:
        inflogging.log("Bad pool XML.", "ERROR")
    xml_pool_name = xml_pool_name[0].value
    if xml_pool_name not in LIBVIRT_CONNECTION.listAllStoragePools(0):
        LIBVIRT_CONNECTION.storagePoolCreateXML(xml_pool, 0)


def clean_domain():
    """Clean existing domain, storage or volume."""

    global LIBVIRT_CONNECTION
    if not LIBVIRT_CONNECTION:
        return

    domains = LIBVIRT_CONNECTION.listAllDomains(0)
    domains = [(domain.name(), domain) for domain in domains]

    if "alfa-infinity" in domains:
        dom = conn.lookupByName("alfa-infinity")
        dom.destroy()

    pools = conn.listAllStoragePools(0)
    pools = [pool.name() for pool in pools]
    if "infinity-disks" in pools:
        pool = conn.storagePoolLookupByName("infinity-disks")

        vols = pool.listVolumes()
        if "disk0.qcow2" in vols:
            vol = pool.storageVolLookupByName("disk0.qcow2")
            vol.delete(0)
        pool.destroy()


class VirtualMachine(object):
    """Class for preserving information about virtual machines."""

    def __init__(self, domain, port, storage, storage_path, pool):
        """Initializes VirtualMachine object.

        Keyword arguments:
        domain -- libvirt.Domain object
        port -- port number of display (for VNC use)
        storage -- libvirt.StorageVolume object
        storage_path -- filepath to storage image
        pool -- libvirt.StoragePool object

        """
        self.domain = domain
        self.port = port
        self.storage = storage
        self.storage_path = storage_path
        self.pool = pool

    def delete(self):
        """Destroy VirtualMachine object, deleting associated domain, storage and pool."""
        self.domain.destroy()
        self.storage.delete(0)
        self.pool.destroy()


def create_full_path(path):
    """Return full path to given path.

    If path is relative, return RESOURCES_PATH + path, otherwise return path.
    """
    #TODO: RESOURCES_PATH should be configured for each infinity structure independently
    if os.path.isabs(path):
        fullpath = path
    else:
        fullpath = os.path.join(config.RESOURCES_PATH, path)
    path_dirname = os.path.dirname(fullpath)

    return fullpath, path_dirname


def create_vol(pool, number, path, capacity, path_to_xml="machines/storage.xml"):
    """Create libvirt virtual volume.

    Keyword arguments:
    pool -- livbirt virtual pool object, should be created before
    number -- used in volume ID
    path -- filepath to virtual volume image
    capacity -- volume capacity in gigabytes
    path_to_xml -- path to configuration xml. See create_full_path function.

    """
    fullpath, path_dirname = create_full_path(path_to_xml)

    with open(fullpath) as xmlfile:
        xmldesc = xmlfile.read()

    # format input config file, put ID, filepath and capacity there
    xmldesc = xmldesc.format(number=str(number), path=str(path), capacity=str(capacity))

    vol = pool.createXML(xmldesc, 0)
    return vol


def create_pool(conn, path_to_xml="machines/pool.xml"):
    """Create libvirt virtual pool.

    Keyword arguments:
    conn -- libvirt connection
    path_to_xml -- path to configuration xml. See create_full_path function.

    """
    fullpath, path_dirname = create_full_path(path_to_xml)

    with open(fullpath) as xmlfile:
        xmldesc = xmlfile.read()

    xmldesc = xmldesc.format(path_dirname)

    pool = conn.storagePoolCreateXML(xmldesc, 0)
    return pool


def build(path_to_xml="machines/alfa.xml", ram=2097152):
    """Build virtual machine from configuration file.

    This function creates virtual machine and its pools/vols.
    Configuration should be in xml file, given as argument.
    When path_to_xml argument is relative path, it reads config
    file from RESOURCE_PATH + path_to_xml, else it reads from
    given full path.

    """
    global LIBVIRT_CONNECTION
    fullpath, path_dirname = create_full_path(path_to_xml)

    with open(fullpath) as xmlfile:
        xmldesc = xmlfile.read()

    try:
        # !!! root required
        if not LIBVIRT_CONNECTION:
            LIBVIRT_CONNECTION = libvirt.open("qemu:///system")

        clean_domain(LIBVIRT_CONNECTION)

        pool = create_pool(LIBVIRT_CONNECTION)
        vol = create_vol(pool, 0, path_dirname, 16)

        # change xml configuration to include path
        xmldesc = xmldesc.format(disk_file=vol.path(), iso_file=os.path.join(path_dirname, "image-live.iso"),
                                 ram_size=ram)

        dom = LIBVIRT_CONNECTION.createXML(xmldesc, 0) # creates libvirt domain
        xmlsettings = parseString(dom.XMLDesc(0)) # get XML representation
    except libvirt.libvirtError as e:
        print "#Error in libvirt: ", e
        return None

    try:
        # try to get VNC port, because it's dynamically assigned
        graphics = xmlsettings.getElementsByTagName("graphics")
        if len(graphics) != 1:
            print "#Error: VM XML doesn't contain port number."
            return None

        graphics = graphics[0]
        port = graphics.attributes["port"]
        port = int(port.value)
    except KeyError:
        print "#Error: VM XML doesn't contain port number."
        return None

    virtmachine = VirtualMachine(dom, port, vol, vol.path(), pool)

    return virtmachine


def tearDown(virtmachine):
    """Tears down virtual machine."""
    #TODO: nothing more?
    virtmachine.delete()
