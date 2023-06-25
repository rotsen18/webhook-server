import logging
import os
import subprocess

import settings

logger = logging.getLogger('webhook_server')


class Builder:
    def __init__(self, application):
        self.application = application

    @staticmethod
    def stage_update(app_directory: str):
        app_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        subprocess.run(['git', '-C', app_path, 'pull'])
        return True

    @staticmethod
    def stage_install_requirements(app_directory: str):
        app_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        subprocess.run(['pip', 'install', '-r', os.path.join(app_path, 'requirements.txt')])
        return True

    @staticmethod
    def stage_restart_service(service_name: str):
        return subprocess.run(['systemctl', 'restart', f'{service_name}.service'])

    def run(self, service_name: str = None):
        if service_name:
            services_to_build = [getattr(self.application, service_name)]
        else:
            services_to_build = self.application.services
        directory = services_to_build[0].directory
        try:
            logger.info(f'Updating {self.application} service')
            self.stage_update(app_directory=directory)
            logger.info(f'Installing requirements for {self.application} service')
            self.stage_install_requirements(app_directory=directory)
        except Exception as e:
            logger.debug(e)
            return False
        for service in services_to_build:
            try:
                self.stage_restart_service(service_name=service.service_name)
                logger.info(f'Restarted {service.name}.service')
            except Exception as e:
                logger.debug(f'Failed to restart service {service.service_name}.service')
                logger.debug(e)
        return True
