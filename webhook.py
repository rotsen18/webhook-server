from flask import Flask, request

import settings
import update_runner

app = Flask(__name__)


@app.route('/webhook/github/', methods=['POST'])
def github_webhook():
    application = getattr(settings.target_applications, 'receipt')
    builder = update_runner.Builder(application=application)
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        app.logger.info(f'Received update event from GitHub for {application.name} application')
        builder.run(service_name='bot')
        return 'Webhook received and processed successfully', 200
    else:
        return 'Invalid webhook event', 400


@app.route('/webhook/test/', methods=['GET'])
def test_webhook():
    application = getattr(settings.target_applications, 'receipt')
    builder = update_runner.Builder(application=application)
    return 'Webhook test successful', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
