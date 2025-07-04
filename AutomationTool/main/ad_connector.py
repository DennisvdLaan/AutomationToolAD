from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import logging

class ADConnector:
    def __init__(self, config):
        self.domain = config.get("domain")
        self.username = config.get("username")
        self.password = config.get("password")
        self.dc_ip = config.get("dc_ip")
        self.use_ssl = config.get("use_ssl", False)
        self.conn = None
        self.server = None
        self.logger = logging.getLogger()

    def connect(self):
        self.logger.info(f"Verbinden met AD ({self.dc_ip}) als {self.domain}\\{self.username}")
        try:
            self.server = Server(self.dc_ip, get_info=ALL, use_ssl=self.use_ssl)
            self.conn = Connection(
                self.server,
                user=f"{self.domain}\\{self.username}",
                password=self.password,
                authentication=NTLM,
                auto_bind=True
            )
            self.logger.info("Verbinding gemaakt")
            return True
        except Exception as error:
            self.logger.error(f"Verbinding niet mogelijk, Foutmelding: {error}")
            return False
        
    def domeinnaam(self):
        """Haalt de domeinnamen (bijv. DC=dennis,DC=local)"""
        try:
            return self.conn.server.info.other["defaultNamingContext"][0]
        except Exception as error:
            self.logger.error(f"Kan de domeinnaam niet vinden: {error}")
            return None

    def disconnect(self):
        if self.conn:
            self.conn.unbind()
            self.logger.info("Verbinding gestopt")
