#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2018/02/22

    GoogleStorage là đối tượng hỗ trợ lư trữ trên dịch vụ Google Storage. Nó cung cấp 3 khái niệm:
        Bucket: là một kho lưu trữ file. mối bucket cung cấp 2 khả năng lư trữ lưu trư Label và Object
        Label set: là một tập các label gắn với một Bucket và lưu trữ data theo cơ chế key-value
        Object: là các đối tượng lư trữ của Bucket bao gốm tên(name) Object đường dẫn trong name tự động
        chuyển thành folđer và dữ liệu File

    UML:
                             ,--------------------.
    ,--------------------.   |Bucket              |    ,---------------------.
    |GoogleStorage       |   |--------------------|    |Object               |
    |--------------------|   |--------------------|    |---------------------|
    |--------------------|   |+create_object(name)|    |---------------------|
    |+create_bucket(name)|-->|+add_label()        |--->|+update(local_path)  |
    |+get_bucket(name)   |1.n|+get_label()        |1..n|+download(local_path)|
    `--------------------'   |+remove_label()     |    `---------------------'
                             `--------------------'

    Ví dụ:
        client = GoogleStorage('/resources/configs/credential.json')
        # https://console.cloud.google.com/storage/browser/[bucket-id]/
        bucket = client.create_bucket('my_new_bucket')
        new_object = bucket.create_object('test/first_file_test.png')
        public_url = new_object.upload('/resources/google_storage.png')
        print(public_url)
        # https://console.cloud.google.com/storage/browser/[bucket-id]/test/first_file_test.png
"""
import os
from google.cloud import storage
from google.cloud.storage import Blob


class GoogleStorage:
    def __init__(self, service_account_file_path):
        """
        GoogleStorage là đối tượng hỗ trợ lư trữ trên dịch vụ Google Storage.
        :param service_account_file_path: đường đẫn đến file credential để authen vào Google Storage
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file_path
        self.storage_client = storage.Client()

    def list_buckets(self):
        """
        lấy danh sách bucket có trên google storage
        :return:
        """
        return list(self.storage_client.list_buckets())

    def get_bucket(self, name):
        """
        lấy một bucket có trên google storage
        :param name:
        :return: trả về một đối được Bucket
        """
        bucket = self.storage_client.get_bucket(name)
        return Bucket(bucket)

    def create_bucket(self, name):
        """Creates a new bucket.
        :param name:
        :return: trả về một đối được Bucket đã được tạo
        """
        bucket = self.storage_client.create_bucket(name)
        print('Bucket {} created'.format(bucket.name))
        return Bucket(bucket)

    def delete_bucket(self, name):
        """Deletes a bucket. The bucket must be empty.
        :param name: tên bucket cần xoá
        """
        bucket = self.storage_client.get_bucket(name)
        bucket.delete()
        print('Bucket {} deleted'.format(bucket.name))
        return bucket.exists()


class Bucket:
    def __init__(self, bucket: storage.Bucket):
        self.bucket = bucket
        self.name = bucket.name

    def create_object(self, name):
        """ update files list to folder on bucket.
        :param name: tạo một đối tượng có tên bao gồm cả đường dẫn thư mục ví dụ test/file_test.txt
        :return: trả về Object hỗ trợ upload và download file
        """
        blob = self.bucket.get_blob(name)
        if not blob:
            blob = self.bucket.blob(name)
        return Object(blob)

    def upload_files_to_folder(self, file_names, folder, make_public=True):
        """ update files list to folder on bucket.
        :param file_names: danh sách file path
        :param folder: thư mục trên google storage
        :param make_public: mã định set public cho url
        :return: trả về danh sách url public của google storage
        """
        links = []
        for file_name in file_names:
            head, tail = os.path.split(file_name)
            new_obj = self.create_object(folder + '/' + head)
            links.append(new_obj.upload(file_name, make_public))
            print('upload file {file} to folder {folder} on {bucket}'.format(file=head, folder=folder,
                                                                             bucket=self.name))
        return links

    def download_files_of_folder(self, local_folder_path, folder=None):
        """ update files list to folder on bucket.
        :param local_folder_path: đường đãn đến thư mục tại ổ đĩa
        :param folder: Optional. thư mục trên google storage
        :return: trả về danh sách url public của google storage
        """
        objects = self.list_objects_with_prefix(folder)
        file_names = []
        print('download files of folder {folder} on {bucket}'.format(folder=folder, bucket=self.name))
        for obj in objects:
            head, tail = os.path.split(obj.name)
            file_name = local_folder_path + head
            obj.download(file_name)
            file_names.append(file_name)
        print('have downloaded {len} files'.format(len=len(file_names)))
        return file_names

    def list_objects_with_prefix(self, prefix, delimiter=None):
        """Lists all the blobs in the bucket that begin with the prefix.
        This can be used to list all blobs in a "folder", e.g. "public/".
        The delimiter argument can be used to restrict the results to only the
        "files" in the given "folder". Without the delimiter, the entire tree under
        the prefix is returned. For example, given these blobs:
            /a/1.txt
            /a/b/2.txt
        If you just specify prefix = '/a', you'll get back:
            /a/1.txt
            /a/b/2.txt
        However, if you specify prefix='/a' and delimiter='/', you'll get back:
            /a/1.txt
            :param prefix:  tiền số
            :param delimiter:
            :return: trả về danh sách Object đạt điều kiện
        """
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        result = list()
        print('Objects:')
        for blob in blobs:
            result.append(Object(blob))
            print(blob.name)
        return result

    def get_labels_keys(self):
        """Prints out a bucket's labels.
        đây là bộ dictionary được add cùng với bucket của google storage hoạt động theo cơ chế key-value
        :return: trả về danh sách keys của lable
        """
        labels = self.bucket.labels
        print('get label on {bucket}:{labels}'.format(bucket=self.name, labels=labels))
        return labels.keys()

    def get_label(self, name):
        """Prints out a bucket's labels.
        đây là bộ dictionary được add cùng với bucket của google storage hoạt động theo cơ chế key-value
        :param name:
        :return: trả về value của lable
        """
        labels = self.bucket.labels
        print('get label on {bucket} is {key}:{value}.'.format(bucket=self.bucket.name, key=name, value=labels[name]))
        return labels[name]

    def add_label(self, name, value):
        """Add a label to a bucket.
        đây là bộ dictionary được add cùng với bucket của google storage hoạt động theo cơ chế key-value
        :return: trả về thành công thất bại
        :param name:
        :param value:
        """
        labels = self.bucket.labels
        labels[name] = value
        self.bucket.labels = labels
        self.bucket.patch()

        print('Updated label on {bucket} is {key}:{value}.'.format(bucket=self.name,
                                                                   key=name, value=labels[name]))
        return name in self.bucket.labels

    def remove_label(self, name):
        """Remove a label from a bucket.
        đây là bộ dictionary được add cùng với bucket của google storage hoạt động theo cơ chế key-value
        :return: trả về thành công thất bại
        :param name:
        """
        labels = self.bucket.labels
        if name in labels:
            del labels[name]
        self.bucket.labels = labels
        self.bucket.patch()
        print('Remove labels on {bucket} by {key}.'.format(bucket=self.name, key=name))
        return name in self.bucket.labels


class Object:
    def __init__(self, blob: Blob):
        """
        class Object hỗ trợ upload và download các file từ google storage
        Object là một khái niệm để định nghĩa cho một đối trong bucket.
        nó là một file và có đường dẫn qua thư mục được tự động chuyển thành các folder
        VD: một object có name là: media/music/khong_phai_dang_vua_dau.mp4
        trên google storage tự động chia thành các thư mục
            [bucket]
                media: folder
                    music: folder
                        khong_phai_dang_vua_dau.mp4: file
        :param blob: đối tượng gốc
        """
        self.blob = blob
        self.link = blob.public_url
        self.name = blob.name

    def upload(self, local_path, make_public=True):
        """
        upload một file trên google storage
        :param local_path: đường dẫn dến local file
        :param make_public: set Object thành public
        :return: trả về public url của Object
        """
        self.blob.upload_from_filename(filename=local_path)
        print('File {local_path} uploaded to Object {name}.'.format(local_path=local_path, name=self.name))
        if make_public:
            self.blob.make_public()
        return self.blob.public_url

    def delete(self):
        """
        xoá object khỏi google storage
        :return: trả về thành công thất bại
        """
        self.blob.delete()
        print('Object {} deleted.'.format(self.name))
        return self.blob.exists()

    def download(self, local_path):
        """
        tải file từ google store và lưu xuống ổ đĩa theo local path
        :param local_path:
        :return: trả về thành công thất bại
        """
        self.blob.download_to_filename(local_path)
        print('Object {name} downloaded to {local_path}.'.format(name=self.name, local_path=local_path))
        return os.path.exists(local_path)


# # --------------------------- TEST ---------------------------
if __name__ == '__main__':
    client = GoogleStorage('../../../resources/configs/MicroDream-b7253957aa69.json')
    # https://console.cloud.google.com/storage/browser/[bucket-id]/
    buck = client.get_bucket('nlp_model')
    objs = buck.list_objects_with_prefix('req')
    # Then do other things...
    a_obj = buck.create_object(objs[0].name)
    a_obj.download('test.txt')
    os.remove('test.txt')
    print('file ./test.txt deleted')

    buck.add_label('test', '123456')
    buck.get_labels_keys()
    a_obj = buck.create_object('label/create_service.json')
    a_obj.upload('../../../resources/configs/google_service_account.json')
    print(a_obj.link)
    # obj.delete()
