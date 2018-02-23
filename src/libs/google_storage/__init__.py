#!/usr/bin/python
# -*- coding: utf8 -*-
""" Author: Ly Tuan Anh
    github nick: ongxabeou
    mail: lytuananh2003@gmail.com
    Date created: 2017/12/22
"""
import os
from google.cloud import storage
from google.cloud.storage import Blob


class GoogleStorage:
    def __init__(self, service_account_file_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file_path
        self.storage_client = storage.Client()

    def list_buckets(self):
        return list(self.storage_client.list_buckets())

    def get_bucket(self, name):
        bucket = self.storage_client.get_bucket(name)
        return Bucket(bucket)

    def create_bucket(self, name):
        """Creates a new bucket."""
        bucket = self.storage_client.create_bucket(name)
        print('Bucket {} created'.format(bucket.name))
        return Bucket(bucket)

    def delete_bucket(self, name):
        """Deletes a bucket. The bucket must be empty."""
        bucket = self.storage_client.get_bucket(name)
        bucket.delete()
        print('Bucket {} deleted'.format(bucket.name))


class Bucket:
    def __init__(self, bucket: storage.Bucket):
        self.bucket = bucket

    def create_object(self, name):
        blob = self.bucket.get_blob(name)
        if not blob:
            blob = self.bucket.blob(name)
        return Object(blob)

    def upload_files_to_folder(self, file_names, folder, make_public=True):
        links = []
        for file_name in file_names:
            new_obj = self.create_object(folder + '/' + file_name)
            links.append(new_obj.upload_file(file_name, make_public))
        return links

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
        """
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        result = list()
        print('Blobs:')
        for blob in blobs:
            result.append(Object(blob))
            print(blob.name)
        return result

    def get_labels(self):
        """Prints out a bucket's labels."""
        labels = self.bucket.labels
        print(labels)
        return labels.keys()

    def add_label(self, name, value):
        """Add a label to a bucket."""
        labels = self.bucket.labels
        labels[name] = value
        self.bucket.labels = labels
        self.bucket.patch()

        print('Updated label on {}.'.format(self.bucket.name))
        print(self.bucket.labels)


class Object:
    def __init__(self, blob: Blob):
        self.blob = blob
        self.link = blob.public_url

    def upload_file(self, path, make_public=True):
        self.blob.upload_from_filename(filename=path)
        print('File {} uploaded to {}.'.format(path, self.blob.name))
        if make_public:
            self.blob.make_public()
        return self.blob.public_url

    def delete(self):
        self.blob.delete()
        print('Object {} deleted.'.format(self.blob.name))
        return self.blob.exists()

    def download(self, local_path):
        self.blob.download_to_filename(local_path)
        print('Object {} downloaded to {}.'.format(self.blob.name, local_path))
        return os.path.exists(local_path)


# # --------------------------- TEST ---------------------------
if __name__ == '__main__':
    client = GoogleStorage('../../../resources/configs/MicroDream-b7253957aa69.json')
    # https://console.cloud.google.com/storage/browser/[bucket-id]/
    buck = client.get_bucket('nlp_model')
    objs = buck.list_objects_with_prefix('req')
    # Then do other things...
    obj = buck.create_object(objs[0].blob.name)
    obj.download('test.txt')
    os.remove('test.txt')
    print('file ./test.txt deleted')

    buck.add_label('test', '123456')
    buck.get_labels()
    obj = buck.create_object('label/create_service.json')
    obj.upload_file('../../../resources/configs/google_service_account.json')
    print(obj.link, obj.blob.self_link)
    # obj.delete()

