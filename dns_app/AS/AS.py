import socket
import json
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

UDP_PORT = 53533
DATABASE_FILE = "dns_records.json"
TTL = 10


class AuthoritativeServer:
    def __init__(self, port=UDP_PORT, db_file=DATABASE_FILE):
        self.port = port
        self.db_file = db_file
        self.records = {}
        self.load_records()

    def load_records(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    self.records = json.load(f)
                logging.info(
                    f"Loaded {len(self.records)} DNS records from {self.db_file}")
            else:
                logging.info(
                    f"No database file found at {self.db_file}, starting with empty records")
                self.records = {}
        except Exception as e:
            logging.error(f"Error loading DNS records: {str(e)}")
            self.records = {}

    def save_records(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.records, f, indent=2)
            logging.info(
                f"Saved {len(self.records)} DNS records to {self.db_file}")
        except Exception as e:
            logging.error(f"Error saving DNS records: {str(e)}")

    def register_record(self, name, value, ttl=TTL):
        if name in self.records:
            logging.info(f"Updating existing record for {name}")
        else:
            logging.info(f"Creating new record for {name}")

        self.records[name] = {
            "value": value,
            "ttl": ttl,
            "timestamp": datetime.now().isoformat()
        }
        self.save_records()
        return True

    def query_record(self, name):
        if name in self.records:
            record = self.records[name]
            logging.info(f"Found record for {name}: {record}")
            return record
        logging.warning(f"No record found for {name}")
        return None

    def parse_message(self, message):
        lines = message.strip().split('\n')
        data = {}

        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                data[key] = value

        return data

    def format_query_response(self, name, value, ttl=TTL):
        return f"TYPE=A\nNAME={name}\nVALUE={value}\nTTL={ttl}"

    def handle_client(self, data, addr):
        message = data.decode('utf-8')
        logging.info(f"Received message from {addr}: {message}")

        parsed = self.parse_message(message)

        if 'TYPE' in parsed and 'NAME' in parsed and 'VALUE' in parsed:
            name = parsed['NAME']
            value = parsed['VALUE']
            ttl = int(parsed.get('TTL', TTL))

            self.register_record(name, value, ttl)
            logging.info(
                f"Registered DNS record: {name} -> {value} (TTL: {ttl})")

            return None

        elif 'TYPE' in parsed and 'NAME' in parsed:
            if parsed['TYPE'] == 'A':
                name = parsed['NAME']
                record = self.query_record(name)

                if record:
                    response = self.format_query_response(
                        name, record['value'], record['ttl'])
                    logging.info(
                        f"Responding to query for {name} with {response}")
                    return response
                else:
                    logging.warning(f"No record found for query: {name}")
                    return None
        else:
            logging.warning(f"Unrecognized message format: {message}")
            return None

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        logging.info(f"Authoritative Server started on UDP port {self.port}")

        try:
            while True:
                data, addr = sock.recvfrom(1024)
                logging.info(f"Connection from {addr}")

                response = self.handle_client(data, addr)

                if response:
                    sock.sendto(response.encode(), addr)
        except KeyboardInterrupt:
            logging.info("Server shutting down")
        finally:
            sock.close()
            self.save_records()


if __name__ == "__main__":
    server = AuthoritativeServer()
    server.start()
