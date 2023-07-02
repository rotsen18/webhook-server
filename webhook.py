import logging

from flask import Flask, request

import application_parser
import update_runner

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
    builder = update_runner.Builder(application=application)
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        app.logger.info(f'Received update event from GitHub for {application.name} application')
        builder.run()
        return 'Webhook received and processed successfully', 200
    elif event_type == 'ping':
        return 'Webhook received successfully', 200
    else:
        return 'Invalid webhook event', 400


@app.route('/webhook/test/', methods=['GET', 'POST'])
def test_webhook():
    repo_name = request.json['repository']['name']
    app.logger.info(f'Received webhook event from GitHub for {repo_name} repository')
    application = getattr(application_parser.target_applications, 'receipt')
    builder = update_runner.Builder(application=application)
    return 'Webhook test successful', 200


@app.route('/', methods=['GET', 'POST'])
def index():
    service_statuses = []
    for application in application_parser.target_applications.applications:
        app_services = application.services
        for service in app_services:
            service_statuses.append(f'<h3>{service}</h3>')
    return '\n'.join(service_statuses)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100)
