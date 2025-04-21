from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from fauxdantic import faux_dict


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class ContactInfo(BaseModel):
    email: str
    phone: str
    website: Optional[str] = None


class User(BaseModel):
    name: str
    age: int
    contact: ContactInfo
    address: Address
    description: str
    created_at: datetime
    birth_date: date
    user_id: UUID
    tags: List[str]


def test_context_aware_values() -> None:
    fake_user = faux_dict(User)
    
    # Test basic types
    assert isinstance(fake_user["name"], str)
    assert isinstance(fake_user["age"], int)
    assert isinstance(fake_user["description"], str)
    assert isinstance(fake_user["created_at"], datetime)
    assert isinstance(fake_user["birth_date"], date)
    assert isinstance(fake_user["user_id"], UUID)
    assert isinstance(fake_user["tags"], list)
    assert all(isinstance(tag, str) for tag in fake_user["tags"])
    
    # Test nested models
    contact = fake_user["contact"]
    assert isinstance(contact["email"], str)
    assert "@" in contact["email"]
    assert isinstance(contact["phone"], str)
    assert contact["website"] is None or isinstance(contact["website"], str)
    
    address = fake_user["address"]
    assert isinstance(address["street"], str)
    assert isinstance(address["city"], str)
    assert isinstance(address["state"], str)
    assert isinstance(address["zip_code"], str)
    assert isinstance(address["country"], str)
    
    # Test field name based generation
    assert len(address["street"]) > 5  # Street addresses should be reasonably long
    assert len(address["zip_code"]) >= 5  # ZIP codes should be at least 5 characters
    assert len(contact["phone"]) >= 10  # Phone numbers should be at least 10 digits
    assert len(fake_user["description"]) > 50  # Should be a longer text 