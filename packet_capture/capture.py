

from scapy.all import sniff, get_if_list

from parser import parse_packet



INTERFACE = None



PACKET_COUNT = 0



BPF_FILTER = "ip or ip6 or arp"



def process_packet(packet):

    try:

       
        data = parse_packet(packet)

        
        print(
            f"{data['protocol']:10} | "
            f"{data['source_ip']}:{data['source_port']} "
            f"-> "
            f"{data['destination_ip']}:{data['destination_port']} "
            f"| Length={data['packet_length']}"
        )

        
        if data["tcp_flags"] is not None:

            print(
                f"             TCP Flags: "
                f"{data['tcp_flags']}"
            )

       

        if data["icmp_type"] is not None:

            print(
                f"             ICMP Type: "
                f"{data['icmp_type']} "
                f"| Code: "
                f"{data['icmp_code']}"
            )

        
        

        if data["dns_query"]:

            print(
                f"             DNS Query: "
                f"{data['dns_query']}"
            )

            if data["dns_type"] is not None:

                print(
                    f"             DNS Query Type: "
                    f"{data['dns_type']}"
                )

        
        if data["arp_operation"] is not None:

            print(
                f"             ARP Operation: "
                f"{data['arp_operation']}"
            )

            print(
                f"             MAC: "
                f"{data['source_mac']} "
                f"-> "
                f"{data['destination_mac']}"
            )

        

    except Exception as error:

        print(
            f"Packet processing error: {error}"
        )



def start_capture():

    print()
    print("=" * 75)
    print("                 AI-IDS PACKET CAPTURE")
    print("=" * 75)


    print("\nAvailable Network Interfaces:\n")

    interfaces = get_if_list()

    for interface in interfaces:

        print(f"  [*] {interface}")

    
    print()

    print(
        f"Selected Interface : "
        f"{INTERFACE if INTERFACE else 'Default'}"
    )

    print(
        f"Capture Filter     : {BPF_FILTER}"
    )

    print()
    print("Protocols being monitored:")
    print("  [+] TCP")
    print("  [+] UDP")
    print("  [+] ICMP")
    print("  [+] IPv4")
    print("  [+] IPv6")
    print("  [+] DNS")
    print("  [+] HTTP")
    print("  [+] HTTPS/TLS")
    print("  [+] ARP")

    print()
    print("Starting continuous packet capture...")
    print("Press CTRL+C to stop.")
    print("=" * 75)
    print()

    
    try:

        sniff(

            iface=INTERFACE,

            filter=BPF_FILTER,

            prn=process_packet,

            count=PACKET_COUNT,

            store=False

        )

    except KeyboardInterrupt:

        print()
        print("=" * 75)
        print("Packet capture stopped.")
        print("=" * 75)

    except PermissionError:

        print()
        print("ERROR: Permission denied.")
        print(
            "Run the program with the required "
            "packet-capture privileges."
        )

    except Exception as error:

        print()
        print(f"Capture error: {error}")


if __name__ == "__main__":

    start_capture()