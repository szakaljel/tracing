## Environment:
```
make start_env
```

## Virtualenv
```
make create_venv
```

## Services
```
make start_order_service
make start_delivery_service
make start_notification_service
```

## Architecture
![alt text][arch]

[arch]: ./tracing.png "Architecture"

## Sources
* https://www.jaegertracing.io/docs/1.25/
* https://opentracing.io/docs/overview/what-is-tracing/
* https://github.com/jaegertracing/jaeger-client-python

## UI
* http://localhost:16686/search

## Postman
tracing.postman_collection.json contains postman collection with order service post request