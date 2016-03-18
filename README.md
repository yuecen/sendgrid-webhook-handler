# SendGrid Webhook Handler

For collecting log on SendGrid without using .csv files, we made the webhook handler to receive and index log into Elasticsearch.  

## Quick Start

* ```bash
docker pull yuecen/sendgrid-webhook-handler
```

* Set your IP of Elasticsearch to ```<host_ip>```

* ```bash
docker run -d \
           -e ELASTIC_HOST=<host_ip> \
           --name sg-handler \
           -p 5577:5577 \
           yuecen/sendgrid-webhook-handler
```
