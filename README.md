# SendGrid Webhook Handler

For collecting log from SendGrid without using .csv files, I made this handler to receive and index log into 
Elasticsearch with IP geolocation. 

## Quick Start with Docker

```bash
docker pull yuecen/sendgrid-webhook-handler
```

Set your Elasticsearch IP to ```<host_ip>```

```bash
docker run -d \
           -e ELASTIC_HOST=<host_ip> \
           --name sg-handler \
           -p 5577:5577 \
           yuecen/sendgrid-webhook-handler
```

## Quick Start with Gunucirn

Before you run following script, make sure you have installed all dependent packages listing from ```requirements.txt```.

```bash
gunicorn --workers 5 --log-level INFO --bind 0.0.0.0:5577 wsgi:app
```

Set your Elasticsearch IP by editing the ```handler.ini``` config file.

```bash
[elastic]
host = <host_ip>
...
```

## An Output Example

The handler got a message from SendGrid and indexed to my Elasticsearch. To check the message detail by a curl request.

```bash
curl -XGET "http://127.0.0.1:9200/sendgrid-email-2016-03-18/_search"
```

The response from Elasticsearch shows that it has a nested object with location information, such as continent, latitude 
and longitude

```bash
   "hits": {
      "total": 1,
      "max_score": 1,
      "hits": [
         {
            "_index": "sendgrid-email-2016-03-18",
            "_type": "v1",
            "_id": "AVOKGFfbJ-l6DSDx-FNr",
            "_score": 1,
            "_source": {
               "sg_event_id": "OGU5MGI0ZjUtYmQ1Mi00NGI1LThlZjEtYjY3YzdlMDY4Yjg1",
               "event_time": 1458120402000,
               "ip": "66.249.82.245",
               "@timestamp": "2016-03-18T14:19:24.438724",
               "event": "open",
               "req_geo": {
                  "country": {
                     "code": "AP",
                     "name": "Asia/Pacific Region"
                  },
                  "continent": {
                     "name": "AS"
                  },
                  "location": {
                     "lat": 35,
                     "lon": 105
                  }
               },
               "sg_message_id": "cUJ5EI_pQPyuoTPR4Kke0Q.filter0921p1mdw1.4165.56E9265B32.0",
               "useragent": "Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)",
               "email": "test@gmail.com"
            }
         }
      ]
   }
}
```