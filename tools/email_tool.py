import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool

_drafted_emails: Dict[str, Dict[str, Any]] = {}
_sent_emails: Dict[str, Dict[str, Any]] = {}

class EmailInput(BaseModel):
    action: str = Field(description="Action: 'draft' or 'send'")
    recipient: str = Field(description="Email recipient address")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body text")
    email_id: Optional[str] = Field(default=None, description="Draft ID if sending existing draft")

class EmailTool(BaseTool):
    name = "email"
    description = "Drafts or sends emails. Drafting is automatic; sending requires human approval."
    args_schema = EmailInput
    requires_approval = True  # Tool handles send_email sensitivity

    def _run(self, action: str, recipient: str, subject: str, body: str, email_id: Optional[str] = None) -> Dict[str, Any]:
        eid = email_id or str(uuid.uuid4())[:8]
        
        if action == "draft":
            draft = {
                "email_id": eid,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": "DRAFT"
            }
            _drafted_emails[eid] = draft
            return {"message": "Email draft created successfully", "draft": draft}

        elif action == "send":
            sent_record = {
                "email_id": eid,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": "SENT"
            }
            _sent_emails[eid] = sent_record
            if eid in _drafted_emails:
                del _drafted_emails[eid]
            return {"message": f"Email sent to {recipient} successfully", "email": sent_record}

        else:
            raise ValueError(f"Unsupported email action '{action}'. Valid actions: draft, send.")
