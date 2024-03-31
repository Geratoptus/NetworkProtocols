from scapy.all import *
import socket
import re
import argparse
import prettytable
from scapy.layers.inet import UDP, IP

DESCRIPTION_REGEXP = re.compile(r'^(?:descr|OrgName|owner):\s*(.*)$')
COUNTRY_REGEXP = re.compile(r'^(?:country|Country):\s*(.*)$')
AS_REGEXP = re.compile('^(?:origin|OriginAS|aut-num):\s*(.*)$')


def trace(hostname: str) -> list[str]:
    dst = socket.gethostbyname(hostname)
    ip_addresses = []

    max_hops = 32
    dport = 33434
    end_code = 3

    for ttl in range(max_hops):
        empty_packet = IP(dst=dst, ttl=ttl) / UDP(dport=dport)

        response = sr1(
            empty_packet,
            verbose=0,
            timeout=1
        )

        if response is not None:
            ip_addresses.append(response.src)

            if response.type == end_code:
                break

    return ip_addresses


def parse_rir(log: str) -> Tuple[str, str, str] or None:
    autonomous_station = None
    country = None
    description = None

    for line in log.splitlines():
        if (description_match := DESCRIPTION_REGEXP.match(line)) is not None:
            description = description_match.group(1)
        elif (country_match := COUNTRY_REGEXP.match(line)) is not None:
            country = country_match.group(1)
        elif (autonomous_station_match := AS_REGEXP.match(line)) is not None:
            autonomous_station = autonomous_station_match.group(1)

    if description is None or country is None or autonomous_station is None:
        return None

    return autonomous_station, country, description


def whois(ip: str) -> Tuple[str, str, str] or None:
    rir_hostnames = [
        'whois.ripe.net',
        'whois.arin.net',
        'whois.apnic.net',
        'whois.afrinic.net',
        'whois.lacnic.net'
    ]
    rir_port = 43

    for rir_hostname in rir_hostnames:
        rir_ip = socket.gethostbyname(rir_hostname)

        rir_socket = socket.create_connection((rir_ip, rir_port))
        rir_socket.sendall(f'{ip}\n'.encode())

        log = ""
        while (buffer := rir_socket.recv(1024).decode()) is not None and len(buffer) > 0:
            log += buffer

        rir_socket.close()

        if (result := parse_rir(log)) is not None:
            return result

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname')

    arguments = parser.parse_args()
    ip_list = trace(arguments.hostname)

    info = [(ip, whois(ip)) for ip in ip_list]

    table = prettytable.PrettyTable()
    table.field_names = ['ip', 'as', 'country', 'description']

    for ip, (autonomous_station, country, description) in info:
        table.add_row([ip, autonomous_station, country, description])

    print(table)


if __name__ == '__main__':
    main()
