from datetime import datetime
import os
import time
import pytz


def get_extension(filename):
    return os.path.splitext(filename)[1]


def user_avatar_path(instance, filename):
    """
    Path for storing the profile image of the user
    """
    # file will be uploaded to MEDIA_ROOT/avatars/<username>/<time>.<extension>
    new_filename = str(time.time()).replace(".", "_") + get_extension(filename)

    return "avatars/{0}/{1}".format(instance.username, new_filename)
