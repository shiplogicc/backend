from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

def encrypt_mobile_number(key, mobile_number):
    # Ensure the key is 32 bytes (256 bits) for AES-256
    key = key[:32]
    
    # Generate a random IV (Initialization Vector)
    iv = os.urandom(16)

    # Create an AES-GCM cipher object
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the mobile number
    ciphertext = encryptor.update(mobile_number.encode('utf-8')) + encryptor.finalize()

    # Get the authentication tag
    tag = encryptor.tag

    # Combine IV, ciphertext, and tag for storage or transmission
    encrypted_data = iv + tag + ciphertext

    # Base64 encode the result for easy storage or transmission
    encrypted_data_base64 = base64.b64encode(encrypted_data)

    return encrypted_data_base64

def decrypt_mobile_number(key, encrypted_data_base64):
    # Ensure the key is 32 bytes (256 bits) for AES-256
    key = key[:32]

    # Decode the base64-encoded data
    encrypted_data = base64.b64decode(encrypted_data_base64)

    # Extract IV, tag, and ciphertext
    iv = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    # Create an AES-GCM cipher object
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the mobile number
    decrypted_number = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_number.decode('utf-8')

# Example usage
key = b'SecretKey'  # Replace with a secure key
mobile_number = '1234567890'

# Encrypt the mobile number
encrypted_data = encrypt_mobile_number(key, mobile_number)
print(f'Encrypted Data: {encrypted_data.decode("utf-8")}')

# Decrypt the mobile number
decrypted_number = decrypt_mobile_number(key, encrypted_data)
print(f'Decrypted Mobile Number: {decrypted_number}')

