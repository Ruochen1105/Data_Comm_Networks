from flask import Flask, request
import socket
import requests
import logging

app = Flask(__name__)


@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    if not all([hostname, fs_port, number, as_ip, as_port]):
        logging.error("Missing required parameters")
        return "Bad Request: Missing required parameters", 400

    try:
        fs_port = int(fs_port)
        number = int(number)
        as_port = int(as_port)

        logging.info(f"Querying AS ({as_ip}:{as_port}) for IP of {hostname}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = f"TYPE=A\nNAME={hostname}"
        sock.sendto(message.encode(), (as_ip, as_port))

        sock.settimeout(5)
        response, _ = sock.recvfrom(1024)
        response = response.decode()

        ip_address = None
        for line in response.split('\n'):
            if line.startswith('VALUE='):
                ip_address = line.split('=')[1]
                break

        if not ip_address:
            logging.error("Failed to resolve hostname")
            return "Failed to resolve hostname", 500

        logging.info(
            f"Querying Fibonacci server at {ip_address}:{fs_port} for number {number}")
        url = f"http://{ip_address}:{fs_port}/fibonacci?number={number}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            fibonacci_number = response.text
            return f"{fibonacci_number}", 200
        else:
            logging.error(
                f"Fibonacci server returned status code {response.status_code}")
            return f"Fibonacci server error: {response.status_code}", 500

    except ValueError:
        logging.error("Invalid numeric parameters")
        return "Bad Request: Invalid numeric parameters", 400
    except socket.timeout:
        logging.error("AS server timeout")
        return "AS server timeout", 504
    except requests.RequestException as e:
        logging.error(f"Error connecting to Fibonacci server: {str(e)}")
        return f"Error connecting to Fibonacci server: {str(e)}", 502
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return f"Server error: {str(e)}", 500
    finally:
        if 'sock' in locals():
            sock.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
