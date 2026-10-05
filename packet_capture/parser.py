

from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import ARP
from scapy.layers.dns import DNS



def identify_protocol(packet):

    
    if ARP in packet:
        return "ARP"

    
    if DNS in packet:
        return "DNS"

    
    if TCP in packet:

        source_port = packet[TCP].sport
        destination_port = packet[TCP].dport

        
        if source_port in (80, 8080, 8000) or \
           destination_port in (80, 8080, 8000):

            return "HTTP"

        
        if source_port == 443 or destination_port == 443:

            return "HTTPS/TLS"

        return "TCP"

    
    if UDP in packet:
        return "UDP"

    
    if ICMP in packet:
        return "ICMP"

    
    if IPv6 in packet:
        return "IPv6"

    
    if IP in packet:
        return "IPv4"

    return "OTHER"




def parse_packet(packet):

    protocol = identify_protocol(packet)

    

    source_ip = "-"
    destination_ip = "-"

    source_port = "-"
    destination_port = "-"

    packet_length = len(packet)

    ip_version = None
    ttl = None

    tcp_flags = None

    icmp_type = None
    icmp_code = None

    dns_query = None
    dns_type = None
    dns_class = None

    arp_operation = None
    source_mac = None
    destination_mac = None

    

    if IP in packet:

        source_ip = packet[IP].src
        destination_ip = packet[IP].dst

        ip_version = 4
        ttl = packet[IP].ttl

    

    elif IPv6 in packet:

        source_ip = packet[IPv6].src
        destination_ip = packet[IPv6].dst

        ip_version = 6
        ttl = packet[IPv6].hlim

    

    if ARP in packet:

        source_ip = packet[ARP].psrc
        destination_ip = packet[ARP].pdst

        source_mac = packet[ARP].hwsrc
        destination_mac = packet[ARP].hwdst

        arp_operation = packet[ARP].op

    
    if TCP in packet:

        source_port = packet[TCP].sport
        destination_port = packet[TCP].dport

        tcp_flags = str(packet[TCP].flags)

    

    elif UDP in packet:

        source_port = packet[UDP].sport
        destination_port = packet[UDP].dport

    
    if ICMP in packet:

        icmp_type = packet[ICMP].type
        icmp_code = packet[ICMP].code

    

    if DNS in packet:

        try:

            dns_layer = packet[DNS]

            
            if dns_layer.qd is not None:

                dns_query = dns_layer.qd.qname

                # Convert bytes to string
                if isinstance(dns_query, bytes):

                    dns_query = dns_query.decode(
                        "utf-8",
                        errors="ignore"
                    )

                # Remove final "."
                dns_query = dns_query.rstrip(".")

                # DNS query type
                if hasattr(dns_layer.qd, "qtype"):
                    dns_type = dns_layer.qd.qtype

                # DNS class
                if hasattr(dns_layer.qd, "qclass"):
                    dns_class = dns_layer.qd.qclass

        except Exception as error:

            print(f"DNS parsing error: {error}")

            dns_query = None

   

    return {

        "protocol": protocol,

        "source_ip": source_ip,
        "destination_ip": destination_ip,

        "source_port": source_port,
        "destination_port": destination_port,

        "packet_length": packet_length,

        "ip_version": ip_version,
        "ttl": ttl,

        "tcp_flags": tcp_flags,

        "icmp_type": icmp_type,
        "icmp_code": icmp_code,

        "dns_query": dns_query,
        "dns_type": dns_type,
        "dns_class": dns_class,

        "arp_operation": arp_operation,

        "source_mac": source_mac,
        "destination_mac": destination_mac
    }