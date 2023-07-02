import logging
import os
import subprocess

from flask import Flask, request
from git import Repo

import application_parser
import settings

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


@app.route('/webhook/github/', methods=['POST'])
def github_webhook():
    repo_name = request.json['repository']['name']
    app.logger.info(f'Received webhook event from GitHub for {repo_name} repository')
    application = getattr(application_parser.target_applications, repo_name)
    builder = Builder(application=application)
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        app.logger.info(f'Received update event from GitHub for {application.name} application')
        result = builder.run()
        return f'Webhook received and processed with result: {result}', 200
    elif event_type == 'ping':
        return 'Webhook received successfully', 200
    else:
        return 'Invalid webhook event', 400


@app.route('/webhook/test/', methods=['GET', 'POST'])
def test_webhook():
    repo_name = request.json['repository']['name']
    app.logger.info(f'Received test webhook event from GitHub for {repo_name} repository')
    application = getattr(application_parser.target_applications, 'receipt')
    builder = Builder(application=application)
    return 'Webhook test successful', 200


@app.route('/', methods=['GET', 'POST'])
def index():
    service_statuses = []
    for application in application_parser.target_applications.applications:
        app_services = application.services
        for service in app_services:
            service_statuses.append(f'<h3>{service}</h3>')
    return '\n'.join(service_statuses)


class Builder:
    def __init__(self, application):
        self.application = application

    @staticmethod
    def stage_update(app_directory: str):
        app.logger.debug(f'Start pulling repo from {app_directory} repository')
        repo_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
        app.logger.debug(f'Updated {app_directory} repository')
        return True

    @staticmethod
    def stage_install_requirements(app_directory: str):
        app.logger.debug(f'Start installing requirements for {app_directory} application')
        app_path = os.path.join(settings.BASE_TARGET_APPS_DIR, app_directory)
        venv_path = os.path.join(app_path, 'venv/bin/activate')
        subprocess.run(['source', venv_path])
        subprocess.run(['pip', 'install', '-r', os.path.join(app_path, 'requirements.txt')], capture_output=True)
        app.logger.debug(f'Installed requirements for {app_directory} application')
        return True

    @staticmethod
    def stage_restart_service(service_name: str):
        app.logger.debug(f'Restarting {service_name} service')
        subprocess.run(['systemctl', 'restart', service_name])
        app.logger.debug(f'Restarted {service_name} service')
        return True

    def run(self):
        services_to_build = self.application.services
        directory = self.application.directory
        try:
            self.stage_update(app_directory=directory)
            self.stage_install_requirements(app_directory=directory)
        except Exception as e:
            app.logger.debug(e)
            return False
        for service_name in services_to_build:
            try:
                self.stage_restart_service(service_name=service_name)
                app.logger.info(f'Restarted {service_name}')
            except Exception as e:
                app.logger.debug(f'Failed to restart service {service_name}')
                app.logger.debug(e)
        return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100)
