import sys
from phonenumber_field.modelfields import PhoneNumberField

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


# Sample User model
class User(models.Model):
    chat_id = models.BigAutoField(null=False, primary_key=True)
    fullname = models.CharField(max_length=100, null=True)
    lang = models.CharField(max_length=7, default="ru")
    date_of_created = models.DateTimeField(auto_now_add=True)
    phone = PhoneNumberField(default="+998")

    class Meta:
        db_table = "sys_user"
        # indexes for table (chat_id, fullname)))
        indexes = [
            models.Index(fields=['chat_id', ]),
            models.Index(fields=['fullname', ]),
        ]

    def __str__(self):
        return self.fullname
