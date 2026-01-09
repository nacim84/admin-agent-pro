"""Tool for sending emails with PDF attachments."""

import aiosmtplib
from email.message import EmailMessage
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from execution.core.config import get_settings
import logging
import os

logger = logging.getLogger(__name__)

class EmailSenderTool(BaseTool):
    name: str = "send_email"
    description: str = """
    Send email with PDF attachment following N8n email hierarchy.

    Email hierarchy (STRICT):
    - TO: email_entreprise (ALWAYS)
    - CC: email_professionnel_1, email_professionnel_2, email_client (if available)

    Input format:
    {
        "to": "rn.block.pro@gmail.com",
        "cc": ["rabia.nacim@gmail.com", "comptafournisseurs@alteca.fr"],
        "subject": "Facture FACT-RNBLOCK-022025",
        "body": "Veuillez trouver ci-joint votre facture...",
        "attachments": [{"filename": "facture.pdf", "path": ".tmp/documents/facture.pdf"}]
    }
    """

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Synchronous run not implemented."""
        raise NotImplementedError("Use _arun for EmailSenderTool")

    async def _arun(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Send email with SMTP using aiosmtplib."""
        settings = get_settings()
        
        try:
            msg = EmailMessage()
            msg["From"] = settings.smtp_user
            msg["To"] = to
            if cc:
                msg["Cc"] = ", ".join(cc)
            msg["Subject"] = subject
            msg.set_content(body)

            # Attach PDFs
            if attachments:
                for attachment in attachments:
                    path = attachment["path"]
                    filename = attachment["filename"]
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            pdf_data = f.read()
                        msg.add_attachment(
                            pdf_data,
                            maintype="application",
                            subtype="pdf",
                            filename=filename
                        )
                    else:
                        logger.warning(f"Attachment not found: {path}")

            # Send via SMTP
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                starttls=True if settings.smtp_port == 587 else False,
                use_tls=True if settings.smtp_port == 465 else False,
            )

            recipients = [to]
            if cc:
                recipients.extend(cc)

            logger.info(f"✅ Email sent to {recipients}")
            return {
                "status": "sent",
                "recipients": recipients
            }

        except Exception as e:
            logger.error(f"❌ SMTP Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
