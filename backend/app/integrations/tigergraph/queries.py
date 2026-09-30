"""
Graph Query Abstraction Layer for TigerGraph GSQL queries.
Contains named query definitions and execution helpers for fraud graph pattern detection.
"""

from typing import Dict, Any, List, Optional
from app.integrations.tigergraph.client import TigerGraphClient, tigergraph_client
from app.integrations.tigergraph.exceptions import TigerGraphQueryError
from app.core.logging import logger


class TigerGraphQueryRegistry:
    """Registry and executor for GSQL graph queries used by the Fraud Engine & Investigation Agent."""

    # Pre-defined query names expected to be installed on TigerGraph graph
    QUERY_SHARED_DEVICE_USERS = "find_shared_device_users"
    QUERY_SHARED_IP_USERS = "find_shared_ip_users"
    QUERY_USER_TRANSACTION_NETWORK = "find_user_transaction_network"
    QUERY_SUSPICIOUS_MERCHANT_CONNECTIONS = "find_suspicious_merchant_connections"
    QUERY_RELATED_TRANSACTIONS = "find_related_transactions"
    
    # 12-step Investigation Traversal Queries
    QUERY_GET_CASE_BY_ID = "get_closed_case"
    QUERY_GET_CASE_TRANSACTIONS = "get_case_transactions"
    QUERY_RESOLVE_CARD_CUSTOMER = "resolve_card_customer"
    QUERY_GET_CARD_HISTORY = "get_card_history"
    QUERY_GET_TRANSACTION_CONTEXT = "get_transaction_context"
    QUERY_GET_HISTORICAL_LINKED_CASES = "get_historical_linked_cases"
    QUERY_GET_CASE_EVIDENCE_REQUESTS = "get_case_evidence_requests"

    def __init__(self, client: TigerGraphClient = tigergraph_client) -> None:
        self.client = client

    def run_query(self, query_name: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute an installed GSQL query on TigerGraph with provided parameters.
        Returns graph query response payloads.
        """
        try:
            logger.info(f"Executing TigerGraph query '{query_name}' with parameters: {params}")
            conn = self.client.get_connection()
            result = conn.runInstalledQuery(query_name, params=params)
            return result
        except Exception as e:
            logger.error(f"Error executing TigerGraph query '{query_name}': {e}")
            raise TigerGraphQueryError(f"Query execution failed for '{query_name}'", details=str(e))

    # General helper methods
    def find_shared_device_users(self, device_id: str) -> List[Dict[str, Any]]:
        return self.run_query(self.QUERY_SHARED_DEVICE_USERS, {"device_id": device_id})

    def find_shared_ip_users(self, ip_address: str) -> List[Dict[str, Any]]:
        return self.run_query(self.QUERY_SHARED_IP_USERS, {"ip_address": ip_address})

    def find_user_transaction_network(self, user_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        return self.run_query(self.QUERY_USER_TRANSACTION_NETWORK, {"user_id": user_id, "depth": depth})

    def find_suspicious_merchant_connections(self, merchant_id: str) -> List[Dict[str, Any]]:
        return self.run_query(self.QUERY_SUSPICIOUS_MERCHANT_CONNECTIONS, {"merchant_id": merchant_id})

    def find_related_transactions(self, transaction_id: str) -> List[Dict[str, Any]]:
        return self.run_query(self.QUERY_RELATED_TRANSACTIONS, {"transaction_id": transaction_id})

    # Investigation 12-Step Traversals
    def get_case_by_id(self, case_id: str) -> List[Dict[str, Any]]:
        """Step 1: Load ClosedCase vertex."""
        return self.run_query(self.QUERY_GET_CASE_BY_ID, {"case_id": case_id})

    def get_case_transactions(self, case_id: str) -> List[Dict[str, Any]]:
        """Step 2: Traversal ClosedCase -[INVOLVES]-> Transaction."""
        return self.run_query(self.QUERY_GET_CASE_TRANSACTIONS, {"case_id": case_id})

    def resolve_card_customer(self, transaction_ids: List[str]) -> List[Dict[str, Any]]:
        """Step 3: Traversal Transaction <-[MADE]- Card <-[OWNS]- Customer."""
        return self.run_query(self.QUERY_RESOLVE_CARD_CUSTOMER, {"transaction_ids": transaction_ids})

    def get_card_history(self, card_ids: List[str]) -> List[Dict[str, Any]]:
        """Step 4: Fetch prior transactions on linked cards."""
        return self.run_query(self.QUERY_GET_CARD_HISTORY, {"card_ids": card_ids})

    def get_transaction_context(self, transaction_ids: List[str]) -> List[Dict[str, Any]]:
        """Step 5: Traversal to DeviceProfile, BillingRegion, EmailDomain."""
        return self.run_query(self.QUERY_GET_TRANSACTION_CONTEXT, {"transaction_ids": transaction_ids})

    def get_historical_linked_cases(self, card_ids: List[str]) -> List[Dict[str, Any]]:
        """Step 6: Traversal Card <-[CONNECTED_TO]- ClosedCase."""
        return self.run_query(self.QUERY_GET_HISTORICAL_LINKED_CASES, {"card_ids": card_ids})

    def get_case_evidence_requests(self, case_id: str) -> List[Dict[str, Any]]:
        """Step 7: Traversal EvidenceRequest -[FOR_CASE]-> ClosedCase (strict case boundary)."""
        return self.run_query(self.QUERY_GET_CASE_EVIDENCE_REQUESTS, {"case_id": case_id})


query_registry = TigerGraphQueryRegistry()
