
import logging

from flask import Flask, request, jsonify
from os import environ
from ssl import SSLContext, PROTOCOL_TLSv1_2

from clients import setup_clients
from processor import KSCPProcessor
from webhook import mutate
from injector import KSCPInjector

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

USE_VAULT = environ.get('USE_VAULT') in [ 'true', 'True' ]
USE_GCP = environ.get('USE_GCP') in [ 'true', 'True' ]
USE_AWS = environ.get('USE_AWS') in [ 'true', 'True' ]

# Create injector
injector = KSCPInjector(
  USE_VAULT,
  USE_GCP,
  USE_AWS
)

processor = KSCPProcessor(*setup_clients(
  USE_VAULT,
  USE_GCP,
  USE_AWS
))


@app.route('/mutate', methods=['POST'])
def mutate_webhook():
  allowed, patch = mutate(injector, request.json["request"])

  admission_response = {
      "allowed": allowed,
      "uid": request.json["request"]["uid"],
      "patch": patch,
      "patchtype": "JSONPatch"
  }
  admissionReview = {
      "response": admission_response
  }

  return jsonify(admissionReview)

@app.route("/healthz", methods=["GET"])
def health():
  return jsonify()

if environ.get('USE_PROCESSOR'):
  @app.route('/readsecret', methods=['POST'])
  def read_secret():
      values = processor.process_secret_read(
        request.json['auth'],
        request.json['secret'],
        request.json['namespace']
      )

      return jsonify({'data': values })


if __name__ == '__main__':
  cert_path = environ.get('CERT_FILE_PATH')
  key_path = environ.get('CERT_KEY_PATH')

  if cert_path is None or key_path is None:
    app.run('0.0.0.0', 80, threaded=True)
  else:
    context = SSLContext(PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert_path, key_path)

    app.run('0.0.0.0', 443, threaded=True, debug=True, ssl_context=context)