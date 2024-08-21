import os
import yadisk
from pathlib import Path


def get_yadisk_api_key():
    current_directory = os.getcwd()
    with open(os.path.join(current_directory, "token.txt")) as f:
        return f.readline()


class Uploader:
    def __init__(self, key="", working_dir="unknown_dir"):
        if key == "":
            self.__apikey = get_yadisk_api_key()
        else:
            self.__apikey = key

        self.app_path = f"app:/{working_dir}"
        self.__client = yadisk.Client(token=self.__apikey)
        self.api_valid = False

        if self.__client.check_token(self.__apikey) is False:
            print("token invalid")
        else:
            self.api_valid = True
            self.make_dir(self.app_path)

    def make_dir(self, dir_name) -> bool:
        try:
            self.__client.mkdir(dir_name)  # create dir
            return True
        except yadisk.exceptions.DirectoryExistsError:
            self.__client.remove(dir_name)  # permanently = True # directory exists
            self.make_dir(dir_name)
            return False

    def upload_photos_sync(self, photo_path) -> None:
        if self.api_valid is not False:
            self.__client.upload(photo_path, f"app:/{photo_path.split("projects/")[1]}", overwrite=True)

    def publish_file(self, file_name) -> None:
        if self.api_valid is not False:
            self.__client.publish(f"app:/{file_name.split("projects/")[1]}")

    def get_screenshots_public_path(self) -> list[dict]:
        if self.api_valid is not False:
            meta_data = self.__client.get_meta(
                self.app_path, limit=999
            )  # meta embedded items limit default 20, 0 returns 0
            screenshots_path = []

            for file in meta_data.embedded.items:
                screenshots_path.append(
                    {
                        "id": Path(file.name).stem,
                        "name": file.name,
                        "public_url": file.public_url,
                    }
                )

            return screenshots_path
