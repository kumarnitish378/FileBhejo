import socket
import random
import time

def send_random_data():
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Server IP and port information
    server_ip = '127.0.0.1'  # Replace this with the destination server's IP address
    server_port = 1234  # Replace this with the destination server's port number

    try:
        while True:
            # Generate 4 bytes of random data
            # random_data = bytes([random.randint(48, 55) for _ in range(4)])
            random_data = bytes([53 for _ in range(1)])

            # Send the random data to the server
            udp_socket.sendto(random_data, (server_ip, server_port))
            print(f"Sent: {random_data}")

            # Wait for some time before sending the next data (e.g., 1 second)
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Sending stopped by user.")

    except socket.error as e:
        print(f"Error sending data: {e}")

    finally:
        # Close the socket
        udp_socket.close()

if __name__ == "__main__":
    send_random_data()
