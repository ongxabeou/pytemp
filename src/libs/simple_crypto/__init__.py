#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2018/03/20

    thư viện hỗ trợ mã hoá bao gổm các thuật toán mã hoá như AES, DES, RSA, ElGamal, etc.

    thư viện hỗ trợ mã hoá string, bytes, file
"""

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import DES
from Crypto.PublicKey import RSA

# from Crypto.PublicKey import ElGamal
# from Crypto.Util.number import GCD
# from Crypto.Hash import SHA
from jupyter_client.tests.utils import test_env


class CRYPTO_ALGORITHM:
    AES = 1
    DES = 2
    RSA = 3


class SimpleCrypto(object):
    def __init__(self, password, algorithm=CRYPTO_ALGORITHM.AES, private_key=None):
        """
        Lớp hỗ trợ mã hoá với các thuật toán AES, DES, RSA
        :param password: với trường hợp thuật toán AES, DES password là secret-key
                        nếu là thuật toán RSA là public-key
        :param algorithm: xác lập thuật toán mã hoá
        :param private_key: nếu dùng thuật toán RSA param này phải có giá trị
        """
        self.bs = 16
        self.key = hashlib.sha256(password.encode()).digest()
        self.algorithm = algorithm
        self.private_key = private_key

        self.hdr = b'To your eyes only'
        try:
            self.private_key_obj = RSA.importKey(self.private_key) if self.private_key else None
        except Exception as e:
            raise KeyError('can not import key to RSA error: &s' % e)
        try:
            self.public_key_obj = RSA.importKey(password) \
                if algorithm == CRYPTO_ALGORITHM.RSA else None
        except Exception as e:
            raise KeyError('can not import key to RSA error: &s' % e)

    def encrypt(self, raw):
        if self.algorithm == CRYPTO_ALGORITHM.AES:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return base64.urlsafe_b64encode(iv + cipher.encrypt(bytes(raw, encoding="utf-8")))
        elif self.algorithm == CRYPTO_ALGORITHM.DES:
            raw = self._pad(raw)
            iv = Random.new().read(DES.block_size)
            des = DES.new(self.key, DES.MODE_ECB, iv)
            return self.encode_base64(iv + des.encrypt(raw))
        elif self.algorithm == CRYPTO_ALGORITHM.RSA:
            return self.public_key_obj.encrypt(raw, 'x')[0]
        else:
            raise NotImplementedError('algorithm %s' % self.algorithm)

    def decrypt(self, enc):
        if self.algorithm == CRYPTO_ALGORITHM.AES:
            enc = base64.urlsafe_b64decode(enc)
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self._un_pad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
        if self.algorithm == CRYPTO_ALGORITHM.DES:
            enc = self.decode_base64(enc)
            iv = enc[:DES.block_size]
            cipher = AES.new(self.key, DES.MODE_ECB, iv)
            return self._un_pad(cipher.decrypt(enc[DES.block_size:])).decode('utf-8')
        else:
            raise NotImplementedError('algorithm %s' % self.algorithm)

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s) - 1:])]

    @staticmethod
    def generate_rsa(bits=2048):
        """
        Tạo một cặp khóa RSA với số mũ của 65537 theo định dạng PEM
        :param bits: Chiều dài khóa trong các bit
        :return: khoá cá nhân và khóa công khai
        """
        from Crypto.PublicKey import RSA
        new_key = RSA.generate(bits, e=65537)
        public_key = new_key.publickey().exportKey("PEM")
        private_key = new_key.exportKey("PEM")
        return private_key, public_key

    @staticmethod
    def decode_base64(raw):
        """
        hỗ trợ giải mã base64
        :param raw: dữ liệu gốc
        :return: trả về dữ liệu đã giải mã dạng bytes
        """
        return base64.urlsafe_b64decode(raw)

    @staticmethod
    def encode_base64(raw):
        """
        hỗ trợ mã hoá base64
        :param raw: dữ liệu gốc
        :return: trả về dữ liệu đã mã hoá
        """
        return base64.urlsafe_b64encode(raw)


# --------------------------- TEST ---------------------------
if __name__ == '__main__':
    def test_aes():
        t_aes = SimpleCrypto('123456', CRYPTO_ALGORITHM.AES)
        t_text = t_aes.encrypt("tuan anh").decode('utf-8')
        print(t_text)
        print(t_aes.decrypt(t_text))


    test_aes()
