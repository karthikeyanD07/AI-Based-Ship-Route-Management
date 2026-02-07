"""
Comprehensive database of major world ports.
Data sourced from World Port Index and major shipping routes.
"""
from typing import Dict, Tuple, List, Optional

# Major world ports with coordinates (lat, lon)
WORLD_PORTS: Dict[str, Dict[str, any]] = {
    # North America - Pacific
    "Los Angeles": {"coords": (33.7405, -118.2519), "code": "USLAX", "country": "USA"},
    "Long Beach": {"coords": (33.7701, -118.2148), "code": "USLGB", "country": "USA"},
    "Oakland": {"coords": (37.7947, -122.2806), "code": "USOAK", "country": "USA"},
    "Seattle": {"coords": (47.6019, -122.3381), "code": "USSEA", "country": "USA"},
    "Tacoma": {"coords": (47.2698, -122.4380), "code": "USTIW", "country": "USA"},
    "Vancouver": {"coords": (49.2827, -123.1207), "code": "CAVAN", "country": "Canada"},
    "Prince Rupert": {"coords": (54.3150, -130.3208), "code": "CAPRR", "country": "Canada"},
    
    # North America - Gulf/Atlantic
    "New York": {"coords": (40.6728, -74.1536), "code": "USNYC", "country": "USA"},
    "Newark": {"coords": (40.6844, -74.1547), "code": "USEWR", "country": "USA"},
    "Houston": {"coords": (29.7305, -95.0892), "code": "USHOU", "country": "USA"},
    "Miami": {"coords": (25.7785, -80.1826), "code": "USMIA", "country": "USA"},
    "Savannah": {"coords": (32.0835, -81.0998), "code": "USSAV", "country": "USA"},
    "Charleston": {"coords": (32.7831, -79.9309), "code": "USCHS", "country": "USA"},
    "Norfolk": {"coords": (36.9466, -76.3297), "code": "USORF", "country": "USA"},
    "Baltimore": {"coords": (39.2667, -76.5833), "code": "USBAL", "country": "USA"},
    "New Orleans": {"coords": (29.9511, -90.0715), "code": "USMSY", "country": "USA"},
    
    # South America
    "Santos": {"coords": (-23.9539, -46.3333), "code": "BRSSZ", "country": "Brazil"},
    "Rio de Janeiro": {"coords": (-22.9068, -43.1729), "code": "BRRIO", "country": "Brazil"},
    "Buenos Aires": {"coords": (-34.6037, -58.3816), "code": "ARBUE", "country": "Argentina"},
    "Callao": {"coords": (-12.0564, -77.1278), "code": "PECLL", "country": "Peru"},
    "Valparaiso": {"coords": (-33.0472, -71.6127), "code": "CLVAP", "country": "Chile"},
    "Cartagena": {"coords": (10.3910, -75.4794), "code": "COCTG", "country": "Colombia"},
    
    # Europe - North Sea
    "Rotterdam": {"coords": (51.9225, 4.4792), "code": "NLRTM", "country": "Netherlands"},
    "Amsterdam": {"coords": (52.3667, 4.9000), "code": "NLAMS", "country": "Netherlands"},
    "Antwerp": {"coords": (51.2194, 4.4025), "code": "BEANR", "country": "Belgium"},
    "Hamburg": {"coords": (53.5511, 9.9937), "code": "DEHAM", "country": "Germany"},
    "Bremerhaven": {"coords": (53.5396, 8.5809), "code": "DEBRV", "country": "Germany"},
    "Felixstowe": {"coords": (51.9500, 1.3500), "code": "GBFXT", "country": "UK"},
    "London": {"coords": (51.5074, -0.1278), "code": "GBLON", "country": "UK"},
    "Le Havre": {"coords": (49.4944, 0.1079), "code": "FRLEH", "country": "France"},
    
    # Europe - Mediterranean
    "Barcelona": {"coords": (41.3851, 2.1734), "code": "ESBCN", "country": "Spain"},
    "Valencia": {"coords": (39.4699, -0.3763), "code": "ESVLC", "country": "Spain"},
    "Algeciras": {"coords": (36.1408, -5.4500), "code": "ESALG", "country": "Spain"},
    "Marseille": {"coords": (43.2965, 5.3698), "code": "FRMRS", "country": "France"},
    "Genoa": {"coords": (44.4056, 8.9463), "code": "ITGOA", "country": "Italy"},
    "La Spezia": {"coords": (44.1023, 9.8246), "code": "ITLSP", "country": "Italy"},
    "Piraeus": {"coords": (37.9385, 23.6947), "code": "GRPIR", "country": "Greece"},
    "Istanbul": {"coords": (41.0082, 28.9784), "code": "TRIST", "country": "Turkey"},
    
    # Middle East
    "Dubai": {"coords": (25.2764, 55.2962), "code": "AEDXB", "country": "UAE"},
    "Abu Dhabi": {"coords": (24.4539, 54.3773), "code": "AEAUH", "country": "UAE"},
    "Jeddah": {"coords": (21.5433, 39.1728), "code": "SAJED", "country": "Saudi Arabia"},
    "Doha": {"coords": (25.2854, 51.5310), "code": "QADOH", "country": "Qatar"},
    
    # Africa
    "Port Said": {"coords": (31.2653, 32.3019), "code": "EGPSD", "country": "Egypt"},
    "Suez": {"coords": (29.9668, 32.5498), "code": "EGSUZ", "country": "Egypt"},
    "Durban": {"coords": (-29.8587, 31.0218), "code": "ZADUR", "country": "South Africa"},
    "Cape Town": {"coords": (-33.9249, 18.4241), "code": "ZACPT", "country": "South Africa"},
    "Lagos": {"coords": (6.4550, 3.3841), "code": "NGLOS", "country": "Nigeria"},
    "Mombasa": {"coords": (-4.0435, 39.6682), "code": "KEMBA", "country": "Kenya"},
    
    # Asia - Southeast
    "Singapore": {"coords": (1.2644, 103.8223), "code": "SGSIN", "country": "Singapore"},
    "Port Klang": {"coords": (2.9988, 101.3933), "code": "MYPKG", "country": "Malaysia"},
    "Bangkok": {"coords": (13.7563, 100.5018), "code": "THBKK", "country": "Thailand"},
    "Ho Chi Minh": {"coords": (10.7626, 106.6602), "code": "VNSGN", "country": "Vietnam"},
    "Manila": {"coords": (14.5995, 120.9842), "code": "PHMNL", "country": "Philippines"},
    "Jakarta": {"coords": (-6.2088, 106.8456), "code": "IDJKT", "country": "Indonesia"},
    
    # Asia - East
    "Shanghai": {"coords": (31.2304, 121.4737), "code": "CNSHA", "country": "China"},
    "Ningbo": {"coords": (29.8683, 121.5440), "code": "CNNGB", "country": "China"},
    "Shenzhen": {"coords": (22.5431, 114.0579), "code": "CNSZX", "country": "China"},
    "Guangzhou": {"coords": (23.1291, 113.2644), "code": "CNCAN", "country": "China"},
    "Hong Kong": {"coords": (22.3193, 114.1694), "code": "HKHKG", "country": "Hong Kong"},
    "Qingdao": {"coords": (36.0671, 120.3826), "code": "CNTAO", "country": "China"},
    "Tianjin": {"coords": (39.0842, 117.2010), "code": "CNTSN", "country": "China"},
    "Dalian": {"coords": (38.9140, 121.6147), "code": "CNDLC", "country": "China"},
    "Xiamen": {"coords": (24.4798, 118.0819), "code": "CNXMN", "country": "China"},
    
    "Busan": {"coords": (35.1796, 129.0756), "code": "KRPUS", "country": "South Korea"},
    "Incheon": {"coords": (37.4563, 126.7052), "code": "KRINC", "country": "South Korea"},
    
    "Tokyo": {"coords": (35.6528, 139.8395), "code": "JPTYO", "country": "Japan"},
    "Yokohama": {"coords": (35.4437, 139.6380), "code": "JPYOK", "country": "Japan"},
    "Kobe": {"coords": (34.6901, 135.1955), "code": "JPUKB", "country": "Japan"},
    "Osaka": {"coords": (34.6937, 135.5023), "code": "JPOSA", "country": "Japan"},
    "Nagoya": {"coords": (35.0844, 136.8991), "code": "JPNGO", "country": "Japan"},
    
    # Asia - South
    "Mumbai": {"coords": (18.9375, 72.8347), "code": "INBOM", "country": "India"},
    "Chennai": {"coords": (13.0827, 80.2707), "code": "INMAA", "country": "India"},
    "Kolkata": {"coords": (22.5726, 88.3639), "code": "INCCU", "country": "India"},
    "Nhava Sheva": {"coords": (18.9487, 72.9508), "code": "INNSA", "country": "India"},
    "Karachi": {"coords": (24.8607, 67.0011), "code": "PKKHI", "country": "Pakistan"},
    "Colombo": {"coords": (6.9271, 79.8612), "code": "LKCMB", "country": "Sri Lanka"},
    
    # Oceania
    "Sydney": {"coords": (-33.8688, 151.2093), "code": "AUSYD", "country": "Australia"},
    "Melbourne": {"coords": (-37.8136, 144.9631), "code": "AUMEL", "country": "Australia"},
    "Brisbane": {"coords": (-27.4698, 153.0251), "code": "AUBNE", "country": "Australia"},
    "Auckland": {"coords": (-36.8485, 174.7633), "code": "NZAKL", "country": "New Zealand"},
    
    # Pacific Islands
    "Honolulu": {"coords": (21.3099, -157.8581), "code": "USHNL", "country": "USA"},
    
    # Additional Strategic Ports
    "Panama City": {"coords": (8.9678, -79.5339), "code": "PAPTY", "country": "Panama"},
    "Cristobal": {"coords": (9.3549, -79.9081), "code": "PACRQ", "country": "Panama"},
}


class PortDatabase:
    """Database interface for world ports."""
    
    def __init__(self):
        self.ports = WORLD_PORTS
    
    def get_port_coords(self, port_name: str) -> Tuple[float, float]:
        """Get coordinates for a port by name."""
        if port_name not in self.ports:
            raise ValueError(f"Unknown port: {port_name}. Use search_ports() to find available ports.")
        return self.ports[port_name]["coords"]
    
    def get_port_info(self, port_name: str) -> Dict:
        """Get full information for a port."""
        if port_name not in self.ports:
            raise ValueError(f"Unknown port: {port_name}")
        return {
            "name": port_name,
            **self.ports[port_name]
        }
    
    def search_ports(self, query: str) -> List[str]:
        """Search ports by name (case-insensitive)."""
        query_lower = query.lower()
        return [
            port_name for port_name in self.ports.keys()
            if query_lower in port_name.lower()
        ]
    
    def get_ports_by_country(self, country: str) -> List[str]:
        """Get all ports in a country."""
        return [
            port_name for port_name, data in self.ports.items()
            if data["country"].lower() == country.lower()
        ]
    
    def get_all_ports(self) -> List[str]:
        """Get list of all available port names."""
        return sorted(list(self.ports.keys()))
    
    def get_nearest_port(self, lat: float, lon: float, limit: int = 5) -> List[Dict]:
        """
        Find nearest ports to given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            limit: Maximum number of ports to return
            
        Returns:
            List of port info dicts with distances
        """
        from math import radians, cos, sin, asin, sqrt
        
        def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance in km using Haversine formula."""
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c  # Earth radius in km
            return km
        
        ports_with_distance = []
        for port_name, port_data in self.ports.items():
            port_lat, port_lon = port_data["coords"]
            distance = haversine_distance(lat, lon, port_lat, port_lon)
            ports_with_distance.append({
                "name": port_name,
                "coords": port_data["coords"],
                "code": port_data["code"],
                "country": port_data["country"],
                "distance_km": round(distance, 2)
            })
        
        # Sort by distance and return top N
        ports_with_distance.sort(key=lambda x: x["distance_km"])
        return ports_with_distance[:limit]


# Global instance
port_db = PortDatabase()
