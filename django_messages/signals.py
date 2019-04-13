from django.dispatch import Signal


request_created = Signal()
request_rejected = Signal()
request_canceled = Signal()
request_viewed = Signal()
request_accepted = Signal(providing_args=['from_user', 'to_user'])