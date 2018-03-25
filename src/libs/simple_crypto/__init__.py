#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2018/03/20

    thư viện hỗ trợ mã hoá bao gổm các thuật toán mã hoá như AES, DES, RSA, ElGamal, etc.

    thư viện hỗ trợ mã hoá string, bytes, file
"""
import ast
import base64
import hashlib

import os
from Crypto import Random
from Crypto.Cipher import AES, DES, PKCS1_OAEP
from Crypto.PublicKey import RSA


class CRYPTO_ALGORITHM:
    AES = 1
    DES = 2
    RSA = 3


class PublicKeyFileExists(Exception):
    pass


class SimpleCrypto(object):
    def __init__(self, password=None, algorithm=CRYPTO_ALGORITHM.AES,
                 private_key_file_path=None, public_key_file_path=None):
        """
        Lớp hỗ trợ mã hoá với các thuật toán AES, DES, RSA
        :param private_key_file_path: đường dẫn file PEM
        :param public_key_file_path: đường dẫn file PEM
        :param password: với trường hợp thuật toán AES, DES password là secret-key
                        nếu là thuật toán RSA là public-key
        :param algorithm: xác lập thuật toán mã hoá
        """
        if password and algorithm == CRYPTO_ALGORITHM.AES and len(password) > 16:
            raise KeyError('length of password[%s] not more than 16 char' % password)
        if password and algorithm == CRYPTO_ALGORITHM.DES and len(password) >= 8:
            raise KeyError('length of password[%s] not more than 7 char' % password)
        self.password = password
        self.algorithm = algorithm
        try:
            self.private_key_obj = RSA.importKey(open(private_key_file_path, 'r').read()) \
                if private_key_file_path else None
        except Exception as e:
            raise KeyError('can not import key to RSA error: &s' % e)
        try:
            self.public_key_obj = RSA.importKey(open(public_key_file_path, 'r').read()) \
                if algorithm == CRYPTO_ALGORITHM.RSA else None
        except Exception as e:
            raise KeyError('can not import key to RSA error: &s' % e)

        if algorithm == CRYPTO_ALGORITHM.RSA and self.private_key_obj is None and self.public_key_obj is None:
            raise KeyError('algorithm is CRYPTO_ALGORITHM.RSA must be '
                           'set for private_key_file_path or  public_key_file_path')

    def encrypt(self, raw):
        """
        mã hoá một nội dung bytes hoặc string.
        :param raw: nội dung cần mã hoá
        :return: trả về mảng bytes đã mã hoá
        """
        if self.algorithm == CRYPTO_ALGORITHM.AES:
            key = hashlib.sha256(self.password.encode()).digest()
            raw = self._pad(raw, 16)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return iv + cipher.encrypt(bytes(raw, encoding="utf-8"))
        elif self.algorithm == CRYPTO_ALGORITHM.DES:
            key = self._pad(self.password, 8)
            raw = self._pad(raw, 8)
            des = DES.new(bytes(key, encoding="utf-8"), DES.MODE_ECB)
            return des.encrypt(bytes(raw, encoding="utf-8"))
        elif self.algorithm == CRYPTO_ALGORITHM.RSA:
            if self.public_key_obj is None:
                raise ValueError('can not encrypt because public_key not exists')
            encryptor = PKCS1_OAEP.new(self.public_key_obj)
            encrypted = encryptor.encrypt(bytes(raw, encoding='utf-8'))
            return encrypted
        else:
            raise NotImplementedError('algorithm %s' % self.algorithm)

    def decrypt(self, enc):
        """
        giải mã một nội dung bytes hoặc string.
        :param enc: nội dung cần giải mã
        :return: trả về mảng bytes đã giải mã
        """
        if self.algorithm == CRYPTO_ALGORITHM.AES:
            key = hashlib.sha256(self.password.encode()).digest()
            iv = enc[:AES.block_size]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return self._un_pad(cipher.decrypt(enc[AES.block_size:]))
        if self.algorithm == CRYPTO_ALGORITHM.DES:
            key = self._pad(self.password, 8)
            des = DES.new(bytes(key, encoding="utf-8"), DES.MODE_ECB)
            return self._un_pad(des.decrypt(enc))
        elif self.algorithm == CRYPTO_ALGORITHM.RSA:
            if self.public_key_obj is None:
                raise ValueError('can not decrypt because private_key not exists')
            decryptor = PKCS1_OAEP.new(self.private_key_obj)
            decrypted = decryptor.decrypt(ast.literal_eval(str(enc)))
            return decrypted
        else:
            raise NotImplementedError('algorithm %s' % self.algorithm)

    @staticmethod
    def _pad(s, bs):
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s) - 1:])]

    @staticmethod
    def generate_rsa(private_key_file_path=None, public_key_file_path=None):
        """
        Tạo một cặp khóa RSA với số mũ Random theo định dạng PEM
        :param private_key_file_path:
        :param public_key_file_path:
        :return: khoá cá nhân và khóa công khai
        """
        if private_key_file_path is None or public_key_file_path is None:
            raise KeyError('private_key_file_path and public_key_file_path must be setting')

        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        private, public = key.exportKey(), key.publickey().exportKey()

        if private_key_file_path and public_key_file_path:
            if os.path.isfile(private_key_file_path):
                raise PublicKeyFileExists('public key file not exists')
            SimpleCrypto._create_directories(True, private_key_file_path, public_key_file_path)
            with open(private_key_file_path, 'w') as private_file:
                private_file.write(private.decode('utf-8'))
            with open(public_key_file_path, 'w') as public_file:
                public_file.write(public.decode('utf-8'))

        return private, public

    @staticmethod
    def _create_directories(for_private_key=True, private_key_file_path=None, public_key_file_path=None):
        public_key_path = public_key_file_path.rsplit('/', 1)[0]
        if not os.path.exists(public_key_path):
            os.makedirs(public_key_path)
        if for_private_key:
            private_key_path = private_key_file_path.rsplit('/', 1)[0]
            if not os.path.exists(private_key_path):
                os.makedirs(private_key_path)

    @staticmethod
    def string_to_bytes_by_base64(raw):
        """
        hỗ trợ giải mã base64
        :param raw: dữ liệu gốc
        :return: trả về dữ liệu đã giải mã dạng bytes
        """
        return base64.urlsafe_b64decode(raw)

    @staticmethod
    def bytes_to_string_by_base64(raw):
        """
        hỗ trợ mã hoá base64
        :param raw: dữ liệu gốc
        :return: trả về dữ liệu đã mã hoá
        """
        return base64.urlsafe_b64encode(raw)


# --------------------------- TEST ---------------------------
if __name__ == '__main__':
    def test_crypto(algorithm):
        t_crypto = SimpleCrypto('1234567', algorithm)
        tt = t_crypto.encrypt("t_crypto = SimpleCrypto('1234567', algorithm)")
        print(tt)
        print(t_crypto.decrypt(tt))


    print('-----------------------CRYPTO AES--------------------------')
    test_crypto(CRYPTO_ALGORITHM.AES)
    print('-----------------------CRYPTO DES--------------------------')
    test_crypto(CRYPTO_ALGORITHM.DES)

    try:
        SimpleCrypto.generate_rsa('rsa_key/private.key', 'rsa_key/public.key')
    except Exception as te:
        print(te)
        pass
    print('----------------------CRYPTO RSA---------------------------')
    sc = SimpleCrypto(algorithm=CRYPTO_ALGORITHM.RSA,
                      private_key_file_path='rsa_key/private.key',
                      public_key_file_path='rsa_key/public.key')
    t_text = sc.encrypt("t_crypto = SimpleCrypto('1234567', algorithm)")
    print(t_text)
    print(sc.decrypt(t_text))
