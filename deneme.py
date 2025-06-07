# client.py
import socket
import random

def generate_device_info():
    device_id = f"Device-{random.randint(1000, 9999)}"
    os_list = ["Android", "iOS", "HarmonyOS"]
    android_versions = ["7.0", "8.1", "9", "10", "11", "12", "13"]
    
    os_name = random.choice(os_list)
    android_version = random.choice(android_versions)

    return f"{device_id}|{os_name}|{android_version}"

def main():
    host = "87.106.36.114"  # Sunucunun IP adresi
    port = 9339

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        device_info = generate_device_info()
        print(f"[CLIENT] Gönderilen veri: {device_info}")
        sock.sendall(device_info.encode())

if __name__ == "__main__":
    main()
