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
    |+create_bucket(name)|-->|+patch_labels()     |--->|+update(local_path)  |
    |+get_bucket(name)   |1.n|                    |1..n|+download(local_path)|
    `--------------------'   |                    |    `---------------------'
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
import mimetypes
import os
from abc import abstractmethod
from io import BytesIO

import six
import time
from google import resumable_media
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
        self.labels = bucket.labels

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
            new_obj = self.create_object(os.path.join(folder, head))
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
            file_name = os.path.join(local_folder_path, head)
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
        print('Objects:')
        for blob in blobs:
            print(blob.name)
        return [Object(b) for b in blobs]

    def patch_labels(self):
        """update for all label to a bucket.
        đây là bộ dictionary được add cùng với bucket của google storage hoạt động theo cơ chế key-value
        """
        self.bucket.labels = self.labels
        self.bucket.patch()
        print('Updated label on {bucket}.'.format(bucket=self.name))


class BaseResourceModel:
    """lớp định nghĩa method cơ bản để lư thông tin vào DB sau khi update hoặc delete một file trên google storage."""

    @abstractmethod
    def delete_resource_by_link(self, public_url):
        """
        tìm kiếm dữ liệu theo public url và xoá record trong database sau khi đã xoá được file trên google storage
        :param public_url: đường link google storage của file resource
        """
        pass

    @abstractmethod
    def add_resource(self, public_url):
        """
        thêm thông tin file đã upload lên google storage vào database
        :param public_url: đường link google storage của file resource
        """
        pass


def convert_string_to_bytes(value, encoding='ascii'):
    """Converts a string value to bytes, if necessary.

    Unfortunately, ``six.b`` is insufficient for this task since in
    Python2 it does not modify ``unicode`` objects.

    :type value: str / bytes or unicode
    :param value: The string/bytes value to be converted.

    :type encoding: str
    :param encoding: The encoding to use to convert unicode to bytes. Defaults
                     to "ascii", which will not allow any characters from
                     ordinals larger than 127. Other useful values are
                     "latin-1", which which will only allows byte ordinals
                     (up to 255) and "utf-8", which will encode any unicode
                     that needs to be.

    :rtype: str / bytes
    :returns: The original value converted to bytes (if unicode) or as passed
              in if it started out as bytes.
    :raises TypeError: if the value could not be converted to bytes.
    """
    result = (value.encode(encoding)
              if isinstance(value, six.text_type) else value)
    if isinstance(result, six.binary_type):
        return result
    else:
        raise TypeError('%r could not be converted to bytes' % (value,))


class Object:
    _DEFAULT_CONTENT_TYPE = u'application/octet-stream'

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
        self.content_type = blob.content_type
        self.resource_model: BaseResourceModel = None

    def _get_content_type(self, content_type, filename=None):
        """Determine the content type from the current object.

        The return value will be determined in order of precedence:

        - The value passed in to this method (if not :data:`None`)
        - The value stored on the current blob
        - The default value ('application/octet-stream')

        :type content_type: str
        :param content_type: (Optional) type of content.

        :type filename: str
        :param filename: (Optional) The name of the file where the content
                         is stored.

        :rtype: str
        :returns: Type of content gathered from the object.
        """
        if content_type is None:
            content_type = self.blob.content_type

        if content_type is None and filename is not None:
            content_type, _ = mimetypes.guess_type(filename)

        if content_type is None:
            content_type = self._DEFAULT_CONTENT_TYPE

        return content_type

    def upload_file(self, file_obj, rewind=False, size=None, content_type=None, num_retries=None, make_public=True):
        """
        upload một file trên google storage
        :param file_obj: A file handle open for reading.
        :param rewind: If True, seek to the beginning of the file handle before
                       writing the file to Cloud Storage.
        :param size: The number of bytes to be uploaded (which will be read
                     from ``file_obj``). If not provided, the upload will be
                     concluded once ``file_obj`` is exhausted.
        :param content_type: Optional type of content being uploaded.
        :param num_retries: Number of upload retries. (Deprecated: This
                            argument will be removed in a future release.)
        :param make_public: set Object to public
        :return: trả về public url của Object
        :raises: :class:`~google.cloud.exceptions.GoogleCloudError`
                 if the upload response returns an error status.
        """
        if self.resource_model:
            self.resource_model.add_resource(self.link)
        self.blob.upload_from_file(file_obj=file_obj, rewind=rewind, size=size, content_type=content_type,
                                   num_retries=num_retries)
        if make_public:
            self.blob.make_public()
        # print('File uploaded to Object {name}.'.format(name=self.name))
        return self.link

    def upload(self, local_path, content_type=None, make_public=True):
        """
        upload một file trên google storage
        :param content_type: Optional type of content being uploaded.
        :param local_path: đường dẫn dến local file
        :param make_public: set Object thành public
        :return: trả về public url của Object
        """
        content_type = self._get_content_type(content_type, filename=local_path)

        with open(local_path, 'rb') as file_obj:
            total_bytes = os.fstat(file_obj.fileno()).st_size
            self.link = self.upload_file(file_obj=file_obj, content_type=content_type,
                                         size=total_bytes, make_public=make_public)
        print('File {local_path} uploaded to Object {name}.'.format(local_path=local_path, name=self.name))
        return self.link

    def upload_from_string(self, data, content_type='text/plain', make_public=True):
        """
        upload một file trên google storage
        :param data:
        :param content_type: Optional type of content being uploaded. Defaults to 'text/plain'.
                xem List of MIME types / Internet Media Types: https://www.freeformatter.com/mime-types-list.html
        :param make_public: set Object thành public
        :return: trả về public url của Object
        """
        data = convert_string_to_bytes(data, encoding='utf-8')
        string_buffer = BytesIO(data)
        self.link = self.upload_file(file_obj=string_buffer, content_type=content_type,
                                     size=len(data), make_public=make_public)
        print('File {content_type} uploaded to Object {name}.'.format(content_type=content_type, name=self.name))
        return self.link

    def delete(self):
        """
        xoá object khỏi google storage
        :return: trả về thành công thất bại
        """
        if self.resource_model:
            self.resource_model.delete_resource_by_link(self.link)
        self.blob.delete()
        print('Object {} deleted.'.format(self.name))
        return self.blob.exists()

    def download_file(self, file_obj):
        """
        tải file từ google store và lưu xuống file stream đã tạo sẵn
        :param file_obj: A file handle to which to write the object's data.
        """
        self.blob.download_to_file(file_obj)
        # print('Object {name} downloaded.'.format(name=self.name))

    def download(self, local_path):
        """
        tải file từ google store và lưu xuống ổ đĩa theo local path
        :param local_path: A filename to be passed to ``open``.
        :raises: :class:`google.cloud.exceptions.NotFound`
        :return: trả về thành công thất bại
        """
        try:
            with open(local_path, 'wb') as file_obj:
                self.download_file(file_obj)
        except resumable_media.DataCorruption as exc:
            # Delete the corrupt downloaded file.
            os.remove(local_path)
            raise exc

        updated = self.blob.updated
        if updated is not None:
            mtime = time.mktime(updated.timetuple())
            os.utime(file_obj.name, (mtime, mtime))

        print('Object {name} downloaded to file {file}.'.format(name=self.name, file=local_path))
        return updated is not None

    def download_as_string(self):
        """
        tải file từ google store và trả vè dữ liệu dạng string
        :return: trả về dữ liệu dạng string
        """
        string_buffer = BytesIO()
        self.download_file(string_buffer)
        print('Object {name} downloaded as string.'.format(name=self.name))
        return string_buffer.getvalue()


# --------------------------- TEST ---------------------------
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

    buck.labels['test'] = '123456'
    print(buck.labels.keys())
    buck.patch_labels()
    a_obj = buck.create_object('label/create_service.json')
    a_obj.upload('../../../resources/configs/google_service_account.json')
    print(a_obj.link)
    # obj.delete()
