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
from infexceptions import InfinityException

LIBVIRT_CONNECTION = None
MANAGED_VM_DOMAINS = []
MANAGED_POOL = None
ID = 0


class VirtualMachine(object):
    """Class for preserving information about virtual machines."""

    def __init__(self, domain, ip, port, storage, storage_path):
        """Initializes VirtualMachine object.

        Keyword arguments:
        domain -- libvirt.Domain object
        port -- port number of display (for VNC use)
        storage -- libvirt.StorageVolume object
        storage_path -- filepath to storage image

        """
        self.domain = domain
        self.ip = ip
        self.port = port
        self.storage = storage
        self.storage_path = storage_path

    def delete(self):
        """Destroy VirtualMachine object, deleting associated domain and storage."""
        self.domain.destroy()
        self.storage.delete(0)


def parse_domain_xml(xml, value):
    parsed = parseString(xml)
    elements = parsed.getElementsByTagName(value)
    if len(elements) != 1:
        raise InfinityException("Error when parsing XML: "+value+" is not single element.")
    return elements[0]


def setup_v12n(uri, pool_path):
    global LIBVIRT_CONNECTION, MANAGED_POOL

    # connect to libvirt
    if not LIBVIRT_CONNECTION:
        LIBVIRT_CONNECTION = libvirt.open(uri)  # needs root access

    # create pool for storages
    if MANAGED_POOL:
        return

    xml_file = open(os.path.join(os.path.dirname(__file__), "xml/pool.xml"))
    xml_pool = xml_file.read()
    xml_pool = xml_pool.format(path=pool_path)

    if not os.path.exists(pool_path):
        os.mkdir(pool_path)

    pool_name = parse_domain_xml(xml_pool, "name")
    pool_name = pool_name.firstChild.nodeValue

    storage_pools = LIBVIRT_CONNECTION.listAllStoragePools(0)
    storage_pool_names = [pool.name() for pool in storage_pools]
    if pool_name not in storage_pool_names:
        MANAGED_POOL = (LIBVIRT_CONNECTION.storagePoolCreateXML(xml_pool, 0), pool_path)
    else:
        storage_pool = LIBVIRT_CONNECTION.storagePoolLookupByName(pool_name)
        path = parse_domain_xml(storage_pool.XMLDesc(0), "path")
        path = path.firstChild.nodeValue
        MANAGED_POOL = (storage_pool, path)


def clean_all():
    """Clean all existing domains, storages and pool."""

    global LIBVIRT_CONNECTION, MANAGED_POOL, MANAGED_VM_DOMAINS
    if not LIBVIRT_CONNECTION:
        return

    for domain in MANAGED_VM_DOMAINS:
        domain.destroy()

    if MANAGED_POOL:
        for volume in MANAGED_POOL[0].listAllVolumes(0):
            volume.delete(0)
        MANAGED_POOL[0].destroy()

    MANAGED_POOL = None
    MANAGED_VM_DOMAINS = []


def build(vm_xml, storage_xml, live_medium):
    global LIBVIRT_CONNECTION, MANAGED_POOL, MANAGED_VM_DOMAINS, ID

    if not LIBVIRT_CONNECTION or not MANAGED_POOL:
        raise InfinityException("Not connected to libvirt or pool not created. Run setup_v12n().")

    storage_xml = storage_xml.format(id=ID, path=MANAGED_POOL[1])  # TODO: zkouset zvysit ID, pokud fail
    storage_path = parse_domain_xml(storage_xml, "path")
    storage_path = storage_path.firstChild.nodeValue
    vm_xml = vm_xml.format(id=ID, live_medium=live_medium, disk_path=storage_path)
    ID += 1

    storage = MANAGED_POOL[0].createXML(storage_xml, 0)
    domain = LIBVIRT_CONNECTION.createXML(vm_xml, 0)  # creates libvirt domain
    MANAGED_VM_DOMAINS.append(domain)

    xmlsettings = domain.XMLDesc(0)  # get XML representation

    try:
        # try to get VNC port, because it's dynamically assigned
        graphics = parse_domain_xml(xmlsettings, "graphics")

        port = graphics.attributes["port"]
        port = int(port.value)

        ip = graphics.attributes["listen"]
        ip = ip.value
    except KeyError:
        print "#Error: VM XML doesn't contain port number or IP."
        return None

    virtmachine = VirtualMachine(domain, ip, port, storage, storage.path())

    return virtmachine


def tear_down(virtmachine):
    """Tears down virtual machine."""
    global MANAGED_VM_DOMAINS

    domain = virtmachine.domain
    virtmachine.delete()
    MANAGED_VM_DOMAINS.remove(domain)
