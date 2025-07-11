from __future__ import unicode_literals

from io import BytesIO
import os
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
import mutagen
from nickelodeon.utils import (
    random_key,
    s3_move_object,
    s3_object_delete,
    s3_object_exists,
    s3_get_file,
)


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_prefix = models.CharField(max_length=32, default=random_key, unique=True)

    class Meta:
        verbose_name = "user settings"
        verbose_name_plural = "user settings"

    def save(self, *args, **kwargs):
        if not self.storage_prefix:
            self.storage_prefix = f"{self.username}-{random_key()}"
        super().save(*args, **kwargs)


User.settings = property(
    lambda u: UserSettings.objects.get_or_create(
        user=u, defaults={"storage_prefix": u.username}
    )[0]
)


class MP3Song(models.Model):
    id = models.CharField(default=random_key, max_length=12, primary_key=True)
    filename = models.CharField(
        verbose_name="file name",
        max_length=255,
    )
    duration = models.IntegerField(default=0)
    aac = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def has_extension(self, extension):
        file_path = self.get_file_format_path(extension).encode("utf-8")
        return s3_object_exists(file_path)

    @property
    def has_aac(self):
        return self.has_extension("aac")

    @property
    def has_mp3(self):
        return self.has_extension("mp3")

    def get_absolute_url(self):
        return reverse("song_detail", kwargs={"pk": self.pk})

    def get_download_url(self):
        return reverse("song_download", kwargs={"pk": self.pk})

    @property
    def owner_username(self):
        return self.owner.username

    @property
    def title(self):
        m = re.search(r"(?P<title>[^\/]+$)", self.filename)
        return m.group("title")

    @property
    def available_formats(self):
        return {"mp3": self.has_mp3, "aac": self.has_aac}

    def get_file_format_path(self, extension="mp3"):
        file_path = "{}/{}.{}".format(
            self.owner.settings.storage_prefix, self.filename, extension
        )
        return os.path.normpath(file_path)

    def can_move_to_dest(self, dest):
        new_instance = MP3Song(filename=dest, owner=self.owner)
        for ext, available in self.available_formats.items():
            if available:
                dst = new_instance.get_file_format_path(extension=ext)
                if s3_object_exists(dst):
                    return False
        return True

    def move_file_to(self, dest_filename):
        for ext, available in self.available_formats.items():
            if available:
                src = self.get_file_format_path(extension=ext)
                dst = os.path.normpath(
                    f"{self.owner.settings.storage_prefix}/{dest_filename}.{ext}"
                )
                s3_move_object(src, dst)
        self.filename = dest_filename

    def remove_files(self):
        for ext in ["mp3", "aac"]:
            file_path = self.get_file_format_path(ext).encode("utf-8")
            if s3_object_exists(file_path):
                s3_object_delete(file_path)

    def delete_aac(self):
        if self.has_aac:
            file_path = self.get_file_format_path("aac").encode("utf-8")
            if s3_object_exists(file_path):
                s3_object_delete(file_path)
        if self.aac:
            self.aac = False
            self.save()

    def get_duration(self,force_mp3=False, invalidate_cache=False):
        if self.duration and not invalidate_cache:
            return self.duration

        extension = "aac" if not force_mp3 and self.has_aac else "mp3"

        file = s3_get_file(self.get_file_format_path(extension))
        audio = None
        try:
            audio = mutagen.File(fileobj=BytesIO(file.getvalue()))
        except Exception:
            pass
        if not audio:
            if extension == "aac":
                return self.get_duration(force_mp3=True, invalidate_cache=invalidate_cache)
            else:
                return 0
        self.duration = int(audio.info.length)
        self.save()
        return self.duration
    
    class Meta:
        unique_together = ["owner", "filename"] # TODO: Use constraint
