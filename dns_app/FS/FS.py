from flask import Flask, request, jsonify
import socket
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

hostname = None
ip_address = None
as_ip = None
as_port = None


def calculate_fibonacci(n):
    if n <= 2:
        return 1
    else:
        return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


@app.route('/register', methods=['PUT'])
def register():
    global hostname, ip_address, as_ip, as_port

    try:
        data = request.get_json()

        required_fields = ['hostname', 'ip', 'as_ip', 'as_port']
        if not all(field in data for field in required_fields):
            logging.error("Missing required fields in registration request")
            return jsonify({"error": "Missing required fields"}), 400

        hostname = data['hostname']
        ip_address = data['ip']
        as_ip = data['as_ip']
        as_port = int(data['as_port'])

        logging.info(
            f"Registration request received for {hostname} at {ip_address}")
        logging.info(f"Authoritative server at {as_ip}:{as_port}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip_address}\nTTL=10"

        logging.info(f"Sending DNS registration: {dns_message}")
        sock.sendto(dns_message.encode(), (as_ip, as_port))

        sock.close()

        return jsonify({"message": f"Hostname {hostname} registered successfully"}), 201

    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    try:
        number_param = request.args.get('number')

        if not number_param:
            logging.error("Missing 'number' parameter")
            return "Bad Request: Missing 'number' parameter", 400

        try:
            number = int(number_param)
            assert number >= 1
        except:
            logging.error(f"Invalid number parameter: {number_param}")
            return "Bad Request: 'number' must be a positive integer", 400

        result = calculate_fibonacci(number)
        logging.info(f"Calculated Fibonacci({number}) = {result}")

        return str(result), 200

    except Exception as e:
        logging.error(f"Error processing Fibonacci request: {str(e)}")
        return f"Server error: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
