import logging
from dataclasses import dataclass

import yaml

from settings import APPS_CONFIG_FILE

logger = logging.getLogger('webhook_server')


@dataclass
class Application:
    name: str
    directory: str
    web: str = None
    bot: str = None

    @property
    def services(self):
        result = []
        for service in [self.web, self.bot]:
            if service:
                result.append(service)
        return result


class ServiceApplications:
    all_services = []

    def __init__(self):
        raw_data = self.load_apps(APPS_CONFIG_FILE)
        self.applications = self.parse_applications(raw_data)

    def load_apps(self, file_path):
        logger.info(f'Loading applications from {file_path}')
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def parse_applications(self, apps: dict):
        all_applications = []
        for app_name, app_data in apps.items():
            directory_data, sub_apps_data = app_data
            app_directory = directory_data.get('directory', app_name)
            application = Application(name=app_name, directory=app_directory)

            sub_apps = sub_apps_data.get('services', [])
            for sub_app in sub_apps:
                sub_app_name = next(iter(sub_app.keys()))
                sub_app_service = sub_app[sub_app_name]
                setattr(application, sub_app_name, sub_app_service)
            setattr(self, app_name, application)
            all_applications.append(application)
            logger.info(f'Loaded {app_name} application with services: {application.services}')
        return all_applications


target_applications = ServiceApplications()
