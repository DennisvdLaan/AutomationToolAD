from ldap3 import Server, Connection, ALL, NTLM
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
        self.logger.info(f"Connect to Active Directory ({self.dc_ip}) as {self.domain}\\{self.username}")
        try:
            self.server = Server(self.dc_ip, get_info=ALL, use_ssl=self.use_ssl)
            self.conn = Connection(
                self.server,
                user=f"{self.domain}\\{self.username}",
                password=self.password,
                authentication=NTLM,
                auto_bind=True
            )
            self.logger.info("Connected to AD")
            return True
        except Exception as error:
            self.logger.error(f"Connection not possible; Error: {error}")
            return False

    def domeinnaam(self):
        """Haalt de domeinnaam op (bijv. DC=dennis,DC=local)"""
        try:
            return self.conn.server.info.other["defaultNamingContext"][0]
        except Exception as error:
            self.logger.error(f"Cannot find the domain name: {error}")
            return None

    def get_os_version(self):
        """Haalt unieke OS-versies op van computerobjecten met 'Server' in het OS-veld"""
        try:
            search_base = self.domeinnaam()
            # Zoek alleen computers met 'Server' in het operatingSystem attribuut
            search_filter = "(&(objectClass=computer)(operatingSystem=*Server*))"
            attributes = ["operatingSystem"]

            results = self.conn.extend.standard.paged_search(
                search_base,
                search_filter,
                attributes=attributes,
                paged_size=5,
                generator=False
            )

            os_versions = set()
            for entry in results:
                if 'attributes' in entry and 'operatingSystem' in entry['attributes']:
                    os_attr = entry['attributes']['operatingSystem']
                    if isinstance(os_attr, list) and os_attr:
                        os_value = os_attr[0]
                    else:
                        os_value = os_attr
                    os_versions.add(str(os_value))

            return ", ".join(sorted(os_versions)) if os_versions else "Unknown"
        except Exception as e:
            self.logger.error(f"Cannot find OS Version: {e}")
            return "Unknown"

    def disconnect(self):
        if self.conn:
            self.conn.unbind()
            self.logger.info("Shutdown connection")
