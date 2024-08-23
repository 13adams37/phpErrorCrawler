from urllib.parse import urlparse
from .error_reporter import make_save_report_to_excel
from .uploader import Uploader
from .screenshot import make_screenshots


class AfterCrawlerMethods:
    def __init__(self):
        self.data = {}

    def run(self, income_data, project_name, is_local):
        self.data = income_data
        working_dir = f"{project_name}/"

        errors_with_screenshots = self.get_errors_with_screenshots(
            self.data, working_dir, is_local
        )
        
        print('erros with screenshots', errors_with_screenshots)
        
        make_save_report_to_excel(
            errors_with_screenshots, f"{working_dir}{project_name}"
        )

    def get_errors_with_screenshots(self, data, working_dir, is_local):
        data_with_screenshots = make_screenshots(data, working_dir)
        
        if is_local:
            return data_with_screenshots
        
        disk = Uploader(working_dir=working_dir)

        if disk.api_valid:
            for screenshot in data_with_screenshots:
                if screenshot["screenshot"] != "Ошибка. Без скриншота":
                    disk.upload_photos_sync(screenshot["screenshot"])
                    disk.publish_file(screenshot["screenshot"])

            errors_screenshots = disk.get_screenshots_public_path()

            for first_data in data_with_screenshots:
                for second_data in errors_screenshots:
                    if first_data["id"] == int(second_data["id"]):
                        first_data["screenshot"] = second_data["public_url"]

            return data
        else:
            return data_with_screenshots
