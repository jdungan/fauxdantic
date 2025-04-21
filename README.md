# Fauxdantic

A library for generating fake Pydantic models for testing. Fauxdantic makes it easy to create realistic test data for your Pydantic models.  Pairs well with testing of fastapi endpoints.

## Installation

```bash
poetry add fauxdantic
```

## Features

- Generate fake data for any Pydantic model
- Support for nested models
- Support for common Python types:
  - Basic types (str, int, float, bool)
  - Optional types
  - Lists
  - Dicts
  - UUIDs
  - Datetimes
  - Enums
- Customizable values through keyword arguments
- Generate dictionaries of fake data without creating model instances

## Usage

### Basic Usage

```python
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool

# Generate a fake user
fake_user = faux(User)
print(fake_user)
# Output: name='Smith' age=2045 email='smith@example.com' is_active=True

# Generate a dictionary of fake values
fake_dict = faux_dict(User)
print(fake_dict)
# Output: {'name': 'Smith', 'age': 2045, 'email': 'smith@example.com', 'is_active': True}
```

### Nested Models

```python
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int
    address: Address

# Generate a fake user with nested address
fake_user = faux(User)
print(fake_user)
# Output: name='Smith' age=2045 address=Address(street='123 Main St', city='Anytown', zip_code='12345')

# Generate a dictionary with nested address
fake_dict = faux_dict(User)
print(fake_dict)
# Output: {'name': 'Smith', 'age': 2045, 'address': {'street': '123 Main St', 'city': 'Anytown', 'zip_code': '12345'}}
```

### Optional Fields

```python
from typing import Optional
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class User(BaseModel):
    name: str
    age: Optional[int]
    email: Optional[str]

# Generate a fake user with optional fields
fake_user = faux(User)
print(fake_user)
# Output: name='Smith' age=None email='smith@example.com'

# Generate a dictionary with optional fields
fake_dict = faux_dict(User)
print(fake_dict)
# Output: {'name': 'Smith', 'age': None, 'email': 'smith@example.com'}
```

### Lists and Dicts

```python
from typing import List, Dict
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class User(BaseModel):
    name: str
    tags: List[str]
    preferences: Dict[str, str]

# Generate a fake user with lists and dicts
fake_user = faux(User)
print(fake_user)
# Output: name='Smith' tags=['tag1', 'tag2'] preferences={'key1': 'value1', 'key2': 'value2'}

# Generate a dictionary with lists and dicts
fake_dict = faux_dict(User)
print(fake_dict)
# Output: {'name': 'Smith', 'tags': ['tag1', 'tag2'], 'preferences': {'key1': 'value1', 'key2': 'value2'}}
```

### Custom Values

```python
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class User(BaseModel):
    name: str
    age: int
    email: str

# Generate a fake user with custom values
fake_user = faux(User, name="John Doe", age=30)
print(fake_user)
# Output: name='John Doe' age=30 email='smith@example.com'

# Generate a dictionary with custom values
fake_dict = faux_dict(User, name="John Doe", age=30)
print(fake_dict)
# Output: {'name': 'John Doe', 'age': 30, 'email': 'smith@example.com'}
```

### Enums

```python
from enum import Enum
from pydantic import BaseModel
from fauxdantic import faux, faux_dict

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(BaseModel):
    name: str
    role: UserRole

# Generate a fake user with enum
fake_user = faux(User)
print(fake_user)
# Output: name='Smith' role=<UserRole.ADMIN: 'admin'>

# Generate a dictionary with enum
fake_dict = faux_dict(User)
print(fake_dict)
# Output: {'name': 'Smith', 'role': 'admin'}
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 