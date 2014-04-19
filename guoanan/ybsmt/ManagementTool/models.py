from django.db import models

class usertype(models.Model):
    class Meta:
        permissions = (
            ('super_admin', 'can operate IP_SAN/user/resource/system monitoring'),
            ('admin', 'can operate IP_SAN/resource/system monitoring'),
            ('super_auditor', 'can operate user/audit'),
            ('auditor', 'can operate audit'),
        )