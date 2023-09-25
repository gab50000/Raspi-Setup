import base64
import random

from Crypto.Cipher import AES

SECRET_KEY = b"\x9c\x93\x5b\x48\x73\x0a\x55\x4d\x6b\xfd\x7c\x63\xc8\x86\xa9\x2b\xd3\x90\x19\x8e\xb8\x12\x8a\xfb\xf4\xde\x16\x2b\x8b\x95\xf6\x38"


class FilterModule:
    seed = 0

    def filters(self):
        return {"obscure": self.obscure}

    def obscure(self, text):
        random.seed(self.seed)
        initial_value = random.randbytes(AES.block_size)
        aes = AES.new(
            key=SECRET_KEY, mode=AES.MODE_CTR, initial_value=initial_value, nonce=b""
        )
        encrypted = aes.encrypt(text.encode())
        encoded = base64.urlsafe_b64encode(initial_value + encrypted)
        return encoded.decode("utf-8").rstrip("=")
