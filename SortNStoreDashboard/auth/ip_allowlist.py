"""
IP allowlist enforcement - CIDR-based pre-authentication filtering.

Allows restricting dashboard access to specific IP ranges (e.g., internal network only).
"""

import ipaddress
from typing import List, Tuple, Optional
from flask import request


def parse_cidr_list(cidr_strings: List[str]) -> List:
    """
    Parse list of CIDR strings into ipaddress network objects.
    
    Args:
        cidr_strings: List of CIDR notation strings (e.g., ["192.168.1.0/24", "10.0.0.0/8"])
    
    Returns:
        List of ipaddress.IPv4Network or IPv6Network objects
    
    Raises:
        ValueError if any CIDR string is invalid
    """
    networks = []
    for cidr in cidr_strings:
        try:
            # Support both IPv4 and IPv6
            network = ipaddress.ip_network(cidr.strip(), strict=False)
            networks.append(network)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR notation '{cidr}': {e}")
    return networks


def get_client_ip() -> str:
    """
    Extract client IP from Flask request, handling proxied requests.
    
    Returns:
        Client IP address as string
    """
    # Check X-Forwarded-For for proxied requests (take first IP)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Check X-Real-IP header
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()
    
    # Fall back to direct connection IP
    return request.remote_addr or "unknown"


def is_ip_allowed(ip_str: str, allowed_networks: List) -> Tuple[bool, Optional[str]]:
    """
    Check if an IP address is in any of the allowed CIDR ranges.
    
    Args:
        ip_str: IP address string (e.g., "192.168.1.50")
        allowed_networks: List of ipaddress network objects
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    if not allowed_networks:
        # Empty allowlist means all IPs allowed (feature disabled)
        return True, None
    
    try:
        client_ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False, f"Invalid IP address format: {ip_str}"
    
    # Check if IP is in any allowed network
    for network in allowed_networks:
        if client_ip in network:
            return True, None
    
    return False, f"IP {ip_str} not in allowed ranges"


def check_ip_allowlist() -> Tuple[bool, Optional[str]]:
    """
    Check if current request IP is allowed based on dashboard config.
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config
        
        config = get_dashboard_config()
        allowed_cidrs = config.get('ip_allowlist', [])
        
        # If no allowlist configured, allow all
        if not allowed_cidrs:
            return True, None
        
        # Parse CIDR list
        try:
            allowed_networks = parse_cidr_list(allowed_cidrs)
        except ValueError as e:
            # Log configuration error but don't block access
            print(f"Warning: Invalid IP allowlist configuration: {e}")
            return True, None
        
        # Check client IP
        client_ip = get_client_ip()
        return is_ip_allowed(client_ip, allowed_networks)
    
    except Exception as e:
        # On any error, fail open (allow access) to avoid lockout
        print(f"Warning: IP allowlist check failed: {e}")
        return True, None


def validate_cidr_list(cidr_strings: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate a list of CIDR strings without applying them.
    
    Args:
        cidr_strings: List of CIDR notation strings
    
    Returns:
        (valid: bool, errors: List[str])
    """
    errors = []
    for cidr in cidr_strings:
        try:
            ipaddress.ip_network(cidr.strip(), strict=False)
        except ValueError as e:
            errors.append(f"Invalid CIDR '{cidr}': {str(e)}")
    
    return len(errors) == 0, errors


# Common private network ranges for quick reference
PRIVATE_NETWORKS = {
    "RFC1918_10": "10.0.0.0/8",           # Class A private
    "RFC1918_172": "172.16.0.0/12",       # Class B private
    "RFC1918_192": "192.168.0.0/16",      # Class C private
    "LOCALHOST": "127.0.0.0/8",           # Loopback
    "LINK_LOCAL": "169.254.0.0/16",       # Link-local
}
