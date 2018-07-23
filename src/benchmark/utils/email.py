from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.conf import settings


class EmailService:
    """Send email messages helper class."""
    CONTENT_TYPE = 'html'

    def send_messages(self, subject, template, context, to_emails, attachments=[]):
        """
        Generate and send email message from Django template
        :param subject: Email message subject
        :param template: Email template
        :param to_emails: to email address[es]
        :param attachments: List of attachments - (filename, content, mimetype) triples.
        :return:
        """
        messages = []

        context.update({
            'site': Site.objects.get_current()
        })

        message_template = get_template(template)
        for recipient in to_emails:
            message_content = message_template.render(context)
            message = EmailMessage(subject, message_content, to=[recipient], from_email=settings.EMAIL_FROM_EMAIL)
            message.content_subtype = self.CONTENT_TYPE

            for attach in attachments:
                message.attach(*attach)
            result = message.send()

            messages.append(result)

        return messages
