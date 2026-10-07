"""Structured output: the model must return JSON matching OUR schema.
We declare the schema as a pydantic model; the SDK turns it into JSON
Schema, the API enforces the shape, pydantic validates the values."""

import json
import re
from typing import Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator

client = OpenAI()
MODEL = "gpt-5.4-mini"

EMAIL = """Subject: wrong size AGAIN

Hi, this is Petra Novak (customer since 2019). The boots I got on
Tuesday are a 39, I ordered a 40. Second time this happens. I want the
right size sent this week or my money back. You can reach me on
+44 7700 900 123, mornings are best.  Petra"""


class Ticket(BaseModel):
    customer_name: str
    order_id: str = Field(description="Order number, format ORD-123456")
    issue: Literal["wrong_item", "damaged", "late", "refund", "other"]
    sentiment: Literal["calm", "annoyed", "angry"]
    wants_refund: bool
    phone: Optional[str]

    @field_validator("order_id")
    @classmethod
    def order_id_format(cls, v):
        if not re.fullmatch(r"ORD-\d{6}", v):
            raise ValueError(f"order_id {v!r} is not ORD-123456 shaped")
        return v


def extract(schema, email):
    r = client.chat.completions.parse(
        model=MODEL, response_format=schema,
        messages=[{"role": "system",
                   "content": "Extract a support ticket from the email."},
                  {"role": "user", "content": email}])
    return r.choices[0].message


class TicketV2(Ticket):
    """The fix: admit that the text may not contain an order number."""
    order_id: Optional[str] = Field(
        description="Order number ORD-123456, or null if not in the text")

    @field_validator("order_id")
    @classmethod
    def order_id_format(cls, v):
        if v is not None and not re.fullmatch(r"ORD-\d{6}", v):
            raise ValueError(f"order_id {v!r} is not ORD-123456 shaped")
        return v


if __name__ == "__main__":
    for schema in (Ticket, TicketV2):
        print(f"--- {schema.__name__} ---")
        try:
            msg = extract(schema, EMAIL)
            print(json.dumps(msg.parsed.model_dump(), indent=1))
        except ValidationError as e:
            print("VALIDATION FAILED:", e.errors()[0]["msg"])
            print("model had returned:", repr(e.errors()[0]["input"]))
