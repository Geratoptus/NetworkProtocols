import pickle
import socket
from datetime import datetime, timedelta
from dnslib import DNSRecord, RCODE

CACHE_PATH = 'cache.pickle'
TTL = 10


class DNSCache:
    def __init__(self):
        self.cache = {}

    def add_record(self, key, record):
        self.cache[key] = (record, datetime.now())

    def get_record(self, key):
        if key in self.cache:
            record, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=TTL):
                return record
        else:
            print(f'Запись {key} была удалена')
            del self.cache[key]
        return None

    def save_cache(self):
        with open(CACHE_PATH, 'wb') as file:
            pickle.dump(self.cache, file)

    def load_cache(self):
        try:
            with open(CACHE_PATH, 'rb') as file:
                self.cache = pickle.load(file)
        except FileNotFoundError:
            pass


class DNSServer:
    def __init__(self):
        self.cache = DNSCache()
        self.cache.load_cache()

    def query_solution(self, query_data):
        try:
            query = DNSRecord.parse(query_data)
            key = (query.q.qname, query.a.rtype)
            cache_record = self.cache.get_record(key)

            if cache_record:
                print('Запись была найдена в кэше')
                return cache_record.pack()

            resp = query.send('77.88.8.1', 53, timeout=5)
            resp_record = DNSRecord.parse(resp)
            if resp_record.head.rcode == RCODE.NDERROR:
                self.cache.add_record(key, resp_record)
                self.cache.save_cache()
                print("Запись была добавлена в кэш")
            return resp
        except Exception as e:
            print(f'Ошибка: {e}')
            return

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('localhost', 53))

        print('DNS-сервер работает')
        while True:
            try:
                query_data, addr = server_socket.recvfrom(1024)
                print(f'Получен запрос от: {addr}')
                resp_data = self.query_solution(query_data)
                if resp_data:
                    server_socket.sendto(resp_data, addr)
            except KeyboardInterrupt:
                print('Завершение работы сервера')
                server_socket.close()


def main():
    dns_server = DNSServer()
    dns_server.run()
    

if __name__ == '__main__':
    main()
