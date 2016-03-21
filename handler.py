# -*- coding: utf-8 -*-
import os
import re
import logging
from datetime import datetime
import ConfigParser
import json
from collections import defaultdict

from flask import Flask, request
from elasticsearch import Elasticsearch

import pygeoip


app = Flask(__name__)
app.logger.setLevel(logging.INFO)

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'handler.ini'))

es_host = os.environ['ELASTIC_HOST'] if os.environ.get('ELASTIC_HOST') else config.get('elastic', 'host')
es_port = os.environ['ELASTIC_PORT'] if os.environ.get('ELASTIC_PORT') else config.get('elastic', 'port')
es_index = os.environ['ELASTIC_INDEX'] if os.environ.get('ELASTIC_INDEX') else config.get('elastic', 'index')
es_type = os.environ['ELASTIC_TYPE'] if os.environ.get('ELASTIC_TYPE') else config.get('elastic', 'type')

es = Elasticsearch(hosts=[{'host': es_host, 'port': es_port}])
gi = pygeoip.GeoIP(config.get('geoip', 'db_path'))


@app.route('/s', methods=['POST'])
def handler():
    print request.headers
    data = request.data
    data_dict = json.loads(data)
    for sg_event in data_dict:
        sg_event = set_geo_info(sg_event)
        sg_event = set_email_provider(sg_event)
        sg_event = set_event_time(sg_event)
        sg_event = set_indexed_time(sg_event)
        json_body = json.dumps(sg_event)
        insert_elastic(json_body)
    return "OK"


def set_geo_info(body):
    if 'ip' in body:
        ip = body['ip']
        geo_info = gi.record_by_addr(ip)
        req_geo = defaultdict(lambda: defaultdict())
        if geo_info['continent']:
            req_geo['continent']['name'] = geo_info['continent']
        if geo_info['country_name']:
            req_geo['country']['name'] = geo_info['country_name']
        if geo_info['country_code']:
            req_geo['country']['code'] = geo_info['country_code']
        if geo_info['city']:
            req_geo['city']['name'] = geo_info['city']
        if geo_info['longitude']:
            req_geo['location']['lon'] = geo_info['longitude']
        if geo_info['latitude']:
            req_geo['location']['lat'] = geo_info['latitude']
        body['req_geo'] = req_geo
    return body


def set_email_provider(body):
    if 'email' in body:
        m = re.match(r".*@(?P<provider>.*)", body['email'])
        if m.group('provider'):
            body['provider'] = m.group('provider')
    return body


def set_event_time(body):
    if 'timestamp' in body:
        body['event_time'] = int(str(body['timestamp']) + "000")
        del body['timestamp']
    return body


def set_indexed_time(body):
    body['@timestamp'] = datetime.utcnow().isoformat()
    return body


def insert_elastic(body):
    _rsp = es.index(index=es_index + '-' + str(datetime.now().strftime('%Y-%m-%d')), doc_type=es_type, body=body)
    app.logger.info(_rsp)


if __name__ == '__main__':
    app.run('0.0.0.0', 5577, debug=True)
