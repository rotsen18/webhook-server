import logging
import os
import subprocess

from git import Repo

import settings

logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, application):
        self.application = application

    @staticmethod
    def stage_update(app_directory: str):
        repo_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
        logger.debug(f'Updated {app_directory} repository')
        return True

    @staticmethod
    def stage_install_requirements(app_directory: str):
        app_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        venv_path = os.path.join(app_path, 'venv/bin/activate')
        subprocess.run(['source', venv_path])
        subprocess.run(['pip', 'install', '-r', os.path.join(app_path, 'requirements.txt')])
        logger.debug(f'Installed requirements for {app_directory} application')
        return True

    @staticmethod
    def stage_restart_service(service_name: str):
        subprocess.run(['systemctl', 'restart', service_name])
        logger.debug(f'Restarted {service_name} service')
        return True

    def run(self):
        services_to_build = self.application.services
        directory = self.application.directory
        try:
            logger.info(f'Updating {self.application} service')
            self.stage_update(app_directory=directory)
            logger.info(f'Installing requirements for {self.application} service')
            self.stage_install_requirements(app_directory=directory)
        except Exception as e:
            logger.debug(e)
            return False
        for service_name in services_to_build:
            try:
                self.stage_restart_service(service_name=service_name)
                logger.info(f'Restarted {service_name}')
            except Exception as e:
                logger.debug(f'Failed to restart service {service_name}')
                logger.debug(e)
        return True
