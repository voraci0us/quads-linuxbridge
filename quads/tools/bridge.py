import logging
import pexpect

from quads.config import Config

logger = logging.getLogger(__name__)


class BridgeException(Exception):
    pass


class Bridge(object):
    def __init__(self, ip_address, switch_port, old_vlan, new_vlan):
        self.ip_address = ip_address
        self.switch_port = switch_port
        self.old_vlan = str(old_vlan)
        self.new_vlan = str(new_vlan)
        self.child = None

    def connect(self):
        logger.debug("Connecting to switch: %s" % self.ip_address)
        try:
            self.child = pexpect.spawn(
                "ssh -o StrictHostKeyChecking=no %s@%s"
                % (Config["switch_username"], self.ip_address)
            )
            self.child.expect("#")
        except pexpect.exceptions.TIMEOUT:
            raise BridgeException("Timeout trying to connect via SSH")

    def close(self):
        self.child.close()

    def execute(self, command, expect="#"):
        logger.debug(command)
        try:
            self.child.sendline(command)
            self.child.expect(expect, timeout=120)
        except pexpect.exceptions.TIMEOUT:
            raise BridgeException(f"Timeout trying to execute the command: {command}")

    def set_port(self):
        try:
            self.connect()
            self.execute(f"bridge vlan del dev {self.switch_port} vid {self.old_vlan}")
            self.execute(f"bridge vlan add dev {self.switch_port} vid {self.new_vlan} pvid untagged")
            self.close()
        except BridgeException as ex:
            logger.debug(ex)
            return False
        return True

    def convert_port_public(self):
        try:
            self.connect()
            self.execute(f"bridge vlan del dev {self.switch_port} vid {self.old_vlan}")
            self.execute(f"bridge vlan add dev {self.switch_port} vid {self.new_vlan} pvid untagged")
            self.close()
        except BridgeException as ex:
            logger.debug(ex)
            return False
        return True
