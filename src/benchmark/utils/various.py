from django.contrib.auth import get_user_model

User = get_user_model()

User.__str__ = lambda s: f'{s.first_name} {s.last_name} ({s.email})' if s.first_name else s.email or s.username
