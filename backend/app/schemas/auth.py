"""
Auth Schemas (Pydantic Models for Auth Endpoints)

WHAT IS THIS?
=============
These schemas define the shape of auth-related requests and responses.
They validate data coming in and structure data going out.

PATTERN:
========
- *Request schemas: What the client sends TO the API
- *Response schemas: What the API sends back TO the client

IMPORTANT:
==========
UserResponse does NOT include the password hash.
Never send password data back to the client!
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


