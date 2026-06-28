import subprocess


def encrypt_file(file_path, public_key):
    """Encrypts a file with age using the given public key.
    Returns the path to the encrypted .age file."""
    encrypted_path = f"{file_path}.age"

    cmd = ["age", "-r", public_key, "-o", encrypted_path, file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Encryption failed: {result.stderr}")

    return encrypted_path


def decrypt_file(encrypted_path, identity_file, output_path):
    """Decrypts an .age file using the given identity (private key) file."""
    cmd = ["age", "-d", "-i", identity_file, "-o", output_path, encrypted_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Decryption failed: {result.stderr}")

    return output_path
