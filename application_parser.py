import logging
from dataclasses import dataclass

import yaml

from settings import APPS_CONFIG_FILE

logger = logging.getLogger('webhook_server')


@dataclass
class ApplicationService:
    name: str
    service_name: str
    directory: str


@dataclass
class Application:
    name: str
    web: ApplicationService = None
    bot: ApplicationService = None

    @property
    def services(self):
        return [self.web, self.bot]

    @property
    def services_names(self):
        return [service.name for service in self.services]


class ServiceApplications:
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
            application = Application(name=app_name)
            for sub_app in app_data:
                sub_app_name = next(iter(sub_app.keys()))
                sub_app_service = next(iter(sub_app.values()))
                app_service_data = {'name': sub_app_name}
                for service_data in sub_app_service:
                    app_service_data.update(service_data)
                service = ApplicationService(**app_service_data)
                setattr(application, sub_app_name, service)
            setattr(self, app_name, application)
            all_applications.append(application)
            logger.info(f'Loaded {app_name} application with services: {application.services_names}')
        return all_applications


target_applications = ServiceApplications()
