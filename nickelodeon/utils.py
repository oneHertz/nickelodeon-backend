import base64
import io
import os
import re
import secrets
import struct
import subprocess
import tempfile

import boto3
import botocore
from django.conf import settings
from io import BytesIO

AVAILABLE_FORMATS = {"mp3": "libmp3lame"}


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=botocore.client.Config(signature_version="s3v4", request_checksum_calculation="when_required"),
    )


def bytes_to_str(b):
    if isinstance(b, str):
        return b
    return b.decode("utf-8")


def get_s3_resource():
    return boto3.resource(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )


def s3_create_bucket(bucket_name):
    s3_client = get_s3_client()
    try:
        s3_client.create_bucket(Bucket=bucket_name)
    except (
        s3_client.exceptions.BucketAlreadyOwnedByYou,
        s3_client.exceptions.BucketAlreadyExists,
    ):
        pass


def s3_object_exists(key):
    key = bytes_to_str(key)
    s3 = get_s3_resource()
    try:
        s3.Bucket(settings.S3_BUCKET).Object(key).load()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            # Something else has gone wrong.
            raise
    return True


def s3_object_delete(key):
    key = bytes_to_str(key)
    s3 = get_s3_resource()
    s3.Bucket(settings.S3_BUCKET).Object(key).delete()


def s3_move_object(src, dest):
    src = bytes_to_str(src)
    dest = bytes_to_str(dest)
    s3 = get_s3_resource()
    s3.Bucket(settings.S3_BUCKET).Object(dest).copy_from(
        CopySource=os.path.join(settings.S3_BUCKET, src)
    )
    s3.Bucket(settings.S3_BUCKET).Object(src).delete()


def s3_upload(src, key):
    s3 = get_s3_client()
    s3.upload_fileobj(src, settings.S3_BUCKET, key)


def s3_object_url(key):
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": settings.S3_BUCKET, "Key": key}
    )


def s3_get_file(key):
    s3_buffer = BytesIO()
    out_buffer = BytesIO()
    s3_client = get_s3_client()
    s3_client.download_fileobj(settings.S3_BUCKET, key, s3_buffer)
    return s3_buffer


def random_key():
    rand_bytes = bytes(struct.pack("Q", secrets.randbits(64)))
    b64 = base64.b64encode(rand_bytes).decode("utf-8")
    b64 = b64[:11]
    b64 = b64.replace("+", "-")
    b64 = b64.replace("/", "_")
    return b64
