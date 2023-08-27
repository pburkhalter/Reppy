from websocket import create_connection, WebSocketException
import time

PORT = 8765
IP = "localhost"
MAX_RETRIES = 5  # Maximum number of reconnection attempts
RETRY_DELAY = 5  # Time to wait before each reconnection attempt in seconds


def connect_to_server(ip, port):
    try:
        ws = create_connection(f"ws://{ip}:{port}/")
        return ws
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
        return None


if __name__ == "__main__":
    retries = 0
    ws = None

    while retries < MAX_RETRIES:
        ws = connect_to_server(IP, PORT)
        if ws:
            break
        print(f"Retrying connection in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)
        retries += 1

    if ws is None:
        print("Max retries reached. Exiting.")
        exit(1)

    try:
        while True:
            message = input("Enter a message to send to the print server (or 'exit' to quit): ")
            if message == "exit":
                break

            ws.send(message)
            print(f"Sent message: {message}")

            response = ws.recv()
            print(f"Received message: {response}")

    except WebSocketException as e:
        print(f"WebSocket error occurred: {e}")

    except KeyboardInterrupt:
        print("User interrupted the process.")

    finally:
        if ws:
            ws.close()
            print("WebSocket connection closed.")

