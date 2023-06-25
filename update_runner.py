import subprocess
import os
import settings
from settings import Application
from webhook import app


class Builder:
    def __init__(self, application: Application):
        self.application = application

    @staticmethod
    def git(app_directory: str):
        app_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        subprocess.run(['git', '-C', app_path, 'pull'])
        return True

    @staticmethod
    def restart(service_name: str):
        return subprocess.run(['systemctl', 'restart', f'{service_name}.service'])

    def run(self, service_name: str = None):
        if service_name:
            services_to_build = [getattr(self.application, service_name)]
        else:
            services_to_build = self.application.services
        try:
            app.logger.info(f'Updating {self.application} service')
            self.git(app_directory=services_to_build[0].directory)
        except Exception as e:
            app.logger.debug(e)
            return False
        for service in services_to_build:
            try:
                self.restart(service_name=service.service_name)
                app.logger.info(f'Restarted {service.name}.service')
            except Exception as e:
                app.logger.debug(f'Failed to restart service {service.service_name}.service')
                app.logger.debug(e)
        return True
