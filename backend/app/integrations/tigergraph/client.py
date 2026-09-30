import httpx
from typing import Optional, Any, Dict, List
from app.core.config import settings
from app.core.logging import logger
from app.integrations.tigergraph.exceptions import (
    TigerGraphConnectionError,
    TigerGraphAuthenticationError,
    TigerGraphError,
)

try:
    import pyTigerGraph as tg
except ImportError:
    tg = None  # type: ignore


class TigerGraphClient:
    """
    Manages raw connection lifecycle, authentication, and health checks with TigerGraph server.
    Responsible ONLY for connection management and low-level REST++ operations.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        graph_name: Optional[str] = None,
        secret: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        restpp_port: Optional[int] = None,
        gs_port: Optional[int] = None,
    ) -> None:
        self.host = host or settings.TIGERGRAPH_HOST
        self.graph_name = graph_name or settings.TIGERGRAPH_GRAPH
        self.secret = secret or settings.TIGERGRAPH_SECRET
        self.token = token or settings.TIGERGRAPH_TOKEN
        self.username = username or settings.TIGERGRAPH_USERNAME
        self.password = password or settings.TIGERGRAPH_PASSWORD
        self.restpp_port = restpp_port or settings.TIGERGRAPH_RESTPP_PORT
        self.gs_port = gs_port or settings.TIGERGRAPH_GS_PORT
        
        self._conn: Optional[Any] = None

    def get_connection(self) -> Any:
        """Retrieve active pyTigerGraph connection, creating or authenticating if necessary."""
        if self._conn is not None:
            return self._conn

        if tg is None:
            raise TigerGraphConnectionError(
                "pyTigerGraph library is not installed in the environment."
            )

        try:
            logger.info(f"Initializing TigerGraph connection to graph '{self.graph_name}' at {self.host}")
            
            is_tg_cloud = "tgcloud.io" in self.host.lower()

            conn_kwargs: Dict[str, Any] = {
                "host": self.host,
                "graphname": self.graph_name,
                "tgCloud": is_tg_cloud,
            }

            if self.username:
                conn_kwargs["username"] = self.username
            if self.password:
                conn_kwargs["password"] = self.password
            if self.secret:
                conn_kwargs["gsqlSecret"] = self.secret
            if self.token:
                conn_kwargs["apiToken"] = self.token
            if not is_tg_cloud:
                if self.restpp_port:
                    conn_kwargs["restppPort"] = self.restpp_port
                if self.gs_port:
                    conn_kwargs["gsPort"] = self.gs_port

            conn = tg.TigerGraphConnection(**conn_kwargs)

            # If secret is provided but no token yet, fetch token
            if self.secret and not self.token:
                try:
                    logger.info("Requesting authentication token using secret...")
                    fetched_token = conn.getToken(self.secret)
                    if isinstance(fetched_token, tuple):
                        fetched_token = fetched_token[0]
                    self.token = fetched_token
                    conn.apiToken = self.token
                except Exception as auth_err:
                    logger.warning(f"Note on secret authentication: {auth_err}")

            self._conn = conn
            return self._conn

        except TigerGraphError:
            raise
        except Exception as e:
            logger.error(f"Failed to connect to TigerGraph server at {self.host}: {e}")
            raise TigerGraphConnectionError(f"Connection attempt failed: {str(e)}")

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Generate Authorization headers for RESTPP HTTP requests."""
        headers = {"Accept": "application/json"}
        token = self.token
        if not token and self._conn:
            token = getattr(self._conn, "apiToken", None)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def get_case_evidence_requests(self, case_id: str) -> list:
        """
        Fetch evidence requests for a given case ID using TigerGraph RESTPP API.
        Tries edge traversal first, then vertex filtering fallback.
        """
        headers = await self._get_auth_headers()
        
        # Endpoint 1: Direct RESTPP Edge Traversal (ClosedCase -> EvidenceRequest)
        edge_url = f"{self.host}/restpp/graph/{self.graph_name}/edges/ClosedCase/{case_id}/reverse_FOR_CASE"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(edge_url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"Edge traversal error for case '{case_id}': {e}")

            # Endpoint 2: Direct Vertex Filter Fallback (EvidenceRequest where case_id = case_id)
            vertex_url = f"{self.host}/restpp/graph/{self.graph_name}/vertices/EvidenceRequest"
            params = {"filter": f'case_id="{case_id}"'}
            
            try:
                res = await client.get(vertex_url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("results", [])
            except Exception as e:
                logger.error(f"Vertex filter query error for case '{case_id}': {e}")

        return []

    def check_health(self) -> bool:
        """
        Lightweight connectivity health check.
        Returns True if TigerGraph responds to echo/ping, False otherwise.
        """
        if self._conn is not None:
            try:
                self._conn.echo()
                return True
            except Exception:
                return False

        if tg is None:
            logger.warning("pyTigerGraph not installed. Health check failed.")
            return False

        try:
            conn = self.get_connection()
            res = conn.echo()
            logger.debug(f"TigerGraph health check echo response: {res}")
            return True
        except Exception as e:
            logger.warning(f"TigerGraph health check failed: {e}")
            return False

    def close(self) -> None:
        """Reset cached connection."""
        self._conn = None


tigergraph_client = TigerGraphClient()
