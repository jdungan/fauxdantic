# Fauxdantic

Generate realistic fake data for Pydantic models. Fauxdantic automatically creates test data that respects your model's structure, field types, and constraints.

## Installation

```bash
poetry add fauxdantic
```

## Quick Start

```python
from pydantic import BaseModel
from fauxdantic import faux

class User(BaseModel):
    name: str
    email: str
    age: int

# Generate a fake user instance
fake_user = faux(User)
# User(name='Jennifer Wilson', email='wilson@example.com', age=42)
```

## Features

- **Smart field detection** - Recognizes email, phone, address, and other common fields
- **Constraint-aware** - Respects string lengths, number ranges, and other Pydantic constraints  
- **Zero configuration** - Works immediately with any Pydantic model
- **Nested models** - Handles complex model hierarchies
- **Custom values** - Override specific fields while generating others
- **Deterministic testing** - Seedable for reproducible test data
- **Clear error messages** - Helpful feedback when things go wrong

## Basic Usage

### Generate Model Instances

```python
from fauxdantic import faux

fake_user = faux(User)
# Returns a User instance with generated data
```

### Generate Dictionaries  

```python
from fauxdantic import faux_dict

fake_data = faux_dict(User)
# Returns: {'name': 'John Doe', 'email': 'doe@example.com', 'age': 28}
```

### Override Specific Fields

```python
fake_user = faux(User, name="Alice", age=30)
# User(name='Alice', email='generated@example.com', age=30)
```

## Smart Field Detection

Fauxdantic recognizes field names and generates appropriate data:

```python
class Contact(BaseModel):
    email: str          # Generates valid email addresses
    phone: str          # Generates phone numbers  
    website: str        # Generates URLs
    street: str         # Generates street addresses
    city: str           # Generates city names
    state: str          # Generates state names/abbreviations
    zip_code: str       # Generates postal codes
    description: str    # Generates longer text (50+ chars)

contact = faux(Contact)
# All fields get contextually appropriate fake data
```

## FastAPI Testing

Fauxdantic pairs well with FastAPI endpoint testing:

```python
from fastapi.testclient import TestClient

@app.post("/users", response_model=User)
def create_user(user: User):
    return user

def test_create_user():
    # Generate realistic test data
    user_data = faux_dict(User)
    
    response = client.post("/users", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
```

## Advanced Features

### Constraint Support

Fauxdantic respects Pydantic Field constraints:

```python
from pydantic import Field

class Product(BaseModel):
    name: str = Field(min_length=5, max_length=50)
    price: float = Field(gt=0, le=1000)
    category: str = Field(max_length=20)

product = faux(Product)
# Generated data respects all constraints
```

### Configuration

Configure generation behavior globally:

```python
from fauxdantic import config

# Set collection size ranges
config.set_collection_size_range(2, 5)  # Lists/dicts will have 2-5 items

# Deterministic generation for tests
config.set_seed(42)

# Change faker locale
config.set_locale('ja_JP')
```

### Unique String Generation

Generate unique identifiers with the `<unique>` pattern:

```python
class Order(BaseModel):
    order_id: str = Field(max_length=20)

# Generate unique order IDs
order1 = faux(Order, order_id="ORD<unique>")
order2 = faux(Order, order_id="ORD<unique>") 
# order1.order_id: "ORD1734567890_a1b2c3"
# order2.order_id: "ORD1734567891_d4e5f6"
```

### Error Handling

Fauxdantic provides clear error messages:

```python
# Invalid field names are caught
try:
    faux(User, invalid_field="test")
except InvalidKwargsError as e:
    print(e)
    # Invalid field(s) for User: invalid_field
    # Valid fields: name, email, age

# Unsupported types get helpful suggestions  
from typing import Callable

class BadModel(BaseModel):
    callback: Callable[[int], str]

try:
    faux(BadModel)
except UnsupportedTypeError as e:
    print(e)
    # Unsupported type 'Callable' for field 'callback'
    # Suggestions: Functions/callables are not supported
```

## Supported Types

- **Basic types**: `str`, `int`, `float`, `bool`
- **Temporal**: `datetime`, `date`
- **Identifiers**: `UUID`, Pydantic `UUID4`
- **Collections**: `List[T]`, `Dict[K,V]`, `Set[T]`, `Tuple`
- **Optional**: `Optional[T]`, `Union[T, None]`
- **Enums**: All enum types
- **Nested models**: Other Pydantic models
- **Literals**: `Literal["option1", "option2"]`

## Examples

### Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    email: str
    address: Address
    tags: List[str]

user = faux(User)
# Generates realistic data for all nested fields
```

### Complex Collections

```python
class Order(BaseModel):
    items: List[Dict[str, Union[str, int]]]
    metadata: Dict[str, Any]

order = faux(Order)
# Generates appropriate nested structures
```

### Testing with Factories

```python
def user_factory(**kwargs):
    """Factory function for consistent test users."""
    defaults = {
        "name": "Test User",
        "email": "test@example.com"
    }
    defaults.update(kwargs)
    return faux(User, **defaults)

# Use in tests
def test_user_creation():
    user = user_factory(age=25)
    assert user.age == 25
    assert "@" in user.email
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/fauxdantic

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy src/fauxdantic
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.