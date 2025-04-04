import subprocess


async def generate_wireguard_keys():
    try:
        private_key = subprocess.run(["wg", "genkey"],
                                     capture_output=True,
                                     text=True,
                                     check=True).stdout.strip()
        public_key = subprocess.run(["wg", "pubkey"],
                                    input=private_key,
                                    capture_output=True,
                                    text=True,
                                    check=True).stdout.strip()
        return private_key, public_key
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error generating keys: {e}")

# Ключи получать по id, а удалять по pub_key
async def remove_wireguard_peer(public_key: str, interface: str = "wg0"):
    try:
        result = subprocess.run(
            ["wg", "show", interface, "peers"],
            capture_output=True,
            text=True,
            check=True)
        if public_key not in result.stdout:
            raise RuntimeError(f"Peer {public_key[:10]}... not found in {interface}")
        subprocess.run(["wg", "set", interface, "peer", public_key, "remove"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error deleting user from WireGuard: {e}")

