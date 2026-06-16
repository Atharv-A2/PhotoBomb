from celery import Celery

celery_app = Celery(
    "photobomb",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    broker_transport_options={
        "socket_connect_timeout": 10,
        "retry_on_timeout": True,
    },
)