from typing import Iterable, Optional
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_email(
    subject: str,
    to: Iterable[str],
    template_name: Optional[str] = None,
    context: Optional[dict] = None,
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
    from_email: Optional[str] = None,
    reply_to: Optional[Iterable[str]] = None,
    cc: Optional[Iterable[str]] = None,
    bcc: Optional[Iterable[str]] = None,
    attachments: Optional[list] = None,
) -> bool:
    """
    Universal email sender supporting both HTML and plain text.

    Args:
        subject: Email subject.
        to: List of recipient email addresses.
        template_name: Base template name (without extension).
                       Looks for `<template_name>.html` and `<template_name>.txt`.
        context: Variables for template rendering.
        body_text: Optional plain text body.
        body_html: Optional HTML body.
        from_email: Override sender (defaults to settings.DEFAULT_FROM_EMAIL).
        reply_to, cc, bcc, attachments: Standard email parameters.

    Returns:
        True if sent successfully, False otherwise.
    """

    try:
        # Render templates if provided
        if template_name:
            context = context or {}
            if not body_html:
                body_html = render_to_string(f"{template_name}.html", context)
            if not body_text:
                try:
                    body_text = render_to_string(f"{template_name}.txt", context)
                except Exception:
                    # .txt template is optional
                    body_text = None

        # Fallback: ensure at least plain text exists
        if not body_text and body_html:
            from django.utils.html import strip_tags
            body_text = strip_tags(body_html)
        elif not body_text:
            raise ValueError("Either body_text, body_html, or template_name must be provided")

        email = EmailMultiAlternatives(
            subject=subject.strip(),
            body=body_text.strip(),
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=list(to),
            cc=list(cc or []),
            bcc=list(bcc or []),
            reply_to=list(reply_to or []),
        )

        # Attach HTML alternative
        if body_html:
            email.attach_alternative(body_html, "text/html")

        # Attach files (tuples of (filename, content, mimetype))
        if attachments:
            for attachment in attachments:
                email.attach(*attachment)

        email.send(fail_silently=False)
        return True

    except Exception as e:
        # In production, you’d log this instead of printing
        print(f"Email sending failed: {e}")
        return False
