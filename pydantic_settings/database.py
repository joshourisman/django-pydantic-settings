from typing import Dict, Optional, Tuple

from pydantic import AnyUrl


class DatabaseDsn(AnyUrl):
    def __init__(
        self,
        url: str,
        *,
        scheme: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        tld: Optional[str] = None,
        host_type: str = "domain",
        port: Optional[str] = None,
        path: str = None,
        query: Optional[str] = None,
        fragment: Optional[str] = None,
    ) -> None:
        str.__init__(url)
        self.scheme = scheme
        self.user = user
        self.password = password
        self.host = host
        self.tld = tld
        self.host_type = host_type
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment

    allowed_schemes = {
        "postgres",
        "postgresql",
        "postgis",
        "mssql",
        "mysql",
        "mysqlgis",
        "sqlite",
        "spatialite",
        "oracle",
        "oraclegis",
        "redshift",
    }

    @classmethod
    def validate_host(
        cls, parts: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[str], str, bool]:
        host = None
        for f in ("domain", "ipv4", "ipv6"):
            host = parts[f]
            if host:
                break

        if host is None:
            return None, None, "file", False

        if host.startswith("%2F"):
            return host, None, "socket", False

        return super().validate_host(parts)
