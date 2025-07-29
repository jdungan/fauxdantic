from datetime import datetime
from enum import Enum
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from fauxdantic import faux, faux_dict


class ProductType(str, Enum):
    TYPE_A = "Type A"
    TYPE_B = "Type B"
    VARIANT_001 = "Variant 001"
    VAR_1833 = "VAR 1833"
    VAR_2053 = "VAR 2053"
    VAR_2108 = "VAR 2108"
    VAR_2215 = "VAR 2215"
    VAR_2340 = "VAR 2340"
    VAR_2505 = "VAR 2505"
    VAR_2580 = "VAR 2580"
    VAR_2594GA = "VAR 2594GA"
    VAR_2627 = "VAR 2627"
    VAR_2650 = "VAR 2650"
    VAR_2670 = "VAR 2670"
    ALPHA = "Alpha"
    BETA = "Beta"
    GAMMA = "Gamma"
    DELTA = "Delta"
    EPSILON = "Epsilon"
    SERIES_1926_03 = "19 26.03"


class ExperimentCreate(BaseModel):
    is_control: Union[bool, str, None] = None
    category: str = Field(..., max_length=50)
    batch_year: Union[int, str] = Field(...)
    end_date: Union[datetime, str, None] = None
    facility_name: Union[str, None] = Field(None, max_length=50)
    output_code: str = Field(..., min_length=1, max_length=20)
    completion_date: Union[datetime, str, None] = None
    location_uuid: UUID
    start_date: Union[datetime, str, None] = None
    unit_id: Union[str, None] = Field(None, max_length=20)
    unit_grid_number: str = Field(..., min_length=1, max_length=20)
    grid_range: Union[int, None] = None
    grid_row: Union[int, None] = None
    reference_number: Union[str, None] = Field(None, max_length=20)
    replicate: Union[Literal[1, 2, 3, 4], None] = None
    code: Union[str, None] = Field(None, max_length=20)
    status: Union[str, None] = Field(None, max_length=50)
    experiment_name: str
    experiment_type: Union[str, None] = Field(None, max_length=20)
    product_type: str = Field(..., max_length=50)

    @field_validator("batch_year", mode="before")
    @classmethod
    def validate_batch_year(cls, value: Union[int, str]) -> int:
        try:
            year = int(value)
            if year < 1900 or year > 2100:
                raise ValueError(
                    f"batch_year must be between 1900 and 2100, got {year}"
                )
            return year
        except ValueError as err:
            raise ValueError(f"batch_year error: {value} (error: {err})") from err

    @field_validator("is_control", mode="before")
    @classmethod
    def validate_is_control(cls, value: Union[bool, str, None]) -> Union[bool, None]:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.strip() == "1":
                return True
            if value.strip() == "2":
                return False
        return None

    @field_validator("start_date", "completion_date", "end_date", mode="before")
    @classmethod
    def validate_dates(cls, value: Union[datetime, str, None]) -> Union[datetime, None]:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%m/%d/%Y")
            except ValueError:
                return None


def test_experiment_create_constraint_compliance() -> None:
    """Test that the complex ExperimentCreate model respects all constraints"""
    # Test multiple generations to ensure consistency
    for i in range(10):
        model = faux(ExperimentCreate)

        # Test successful model creation (no validation errors)
        assert isinstance(model, ExperimentCreate)

        # Test string length constraints
        assert len(model.category) <= 50
        assert 1 <= len(model.output_code) <= 20
        assert 1 <= len(model.unit_grid_number) <= 20
        assert len(model.product_type) <= 50

        # Test optional string length constraints
        if model.facility_name is not None:
            assert len(model.facility_name) <= 50
        if model.unit_id is not None:
            assert len(model.unit_id) <= 20
        if model.reference_number is not None:
            assert len(model.reference_number) <= 20
        if model.code is not None:
            assert len(model.code) <= 20
        if model.status is not None:
            assert len(model.status) <= 50
        if model.experiment_type is not None:
            assert len(model.experiment_type) <= 20

        # Test Literal constraints
        if model.replicate is not None:
            assert model.replicate in [1, 2, 3, 4]

        # Test type constraints
        assert isinstance(model.location_uuid, UUID)
        assert isinstance(model.experiment_name, str)

        # Test that batch_year passes validator (should be int and in range)
        assert isinstance(model.batch_year, int)
        assert 1900 <= model.batch_year <= 2100


def test_product_type_enum_generation() -> None:
    """Test that ProductType enum generates valid values from the large enum"""

    class ModelWithProductType(BaseModel):
        product_type_field: ProductType

    for _ in range(20):  # Test multiple times to ensure variety
        model = faux(ModelWithProductType)
        assert isinstance(model.product_type_field, ProductType)
        assert model.product_type_field in list(ProductType)


def test_batch_year_heuristics() -> None:
    """Test that batch_year field uses year heuristics for reasonable values"""

    class BatchYearModel(BaseModel):
        batch_year: int
        birth_year: int
        random_year: int

    for _ in range(10):
        model = faux(BatchYearModel)

        # batch_year should use year heuristics
        current_year = datetime.now().year
        assert 1900 <= model.batch_year <= current_year + 10

        # Other year fields should also use heuristics
        assert 1900 <= model.birth_year <= current_year + 10
        assert 1900 <= model.random_year <= current_year + 10


def test_constraint_vs_old_behavior() -> None:
    """Demonstrate improvement over old random generation"""

    # This model would frequently fail validation with old generation
    class StrictModel(BaseModel):
        short_code: str = Field(..., min_length=3, max_length=5)
        priority: Literal["low", "medium", "high"]
        year: int = Field(..., ge=2020, le=2025)
        percentage: float = Field(..., ge=0.0, le=100.0)

    # Generate multiple instances - all should pass validation
    for _ in range(15):
        model = faux(StrictModel)

        # All these assertions would frequently fail with random generation
        assert 3 <= len(model.short_code) <= 5
        assert model.priority in ["low", "medium", "high"]
        assert 2020 <= model.year <= 2025
        assert 0.0 <= model.percentage <= 100.0


def test_real_world_validation_success() -> None:
    """Test that generated data actually passes validation"""
    # This is the real test - can we create valid instances consistently?

    success_count = 0
    total_attempts = 50

    for _ in range(total_attempts):
        try:
            # This should succeed without manual overrides
            model = faux(ExperimentCreate)

            # Verify it's actually valid by re-validating
            ExperimentCreate.model_validate(model.model_dump())
            success_count += 1

        except Exception as e:
            # If this happens, our constraint handling needs improvement
            print(f"Validation failed: {e}")

    # We should have a very high success rate
    success_rate = success_count / total_attempts
    assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"


def test_mixed_field_types() -> None:
    """Test model with mixed constraint types"""

    class MixedModel(BaseModel):
        literal_field: Literal["a", "b", "c"]
        string_field: str = Field(..., min_length=5, max_length=15)
        int_field: int = Field(..., ge=10, le=50)
        float_field: float = Field(..., gt=0.0, lt=10.0)
        enum_field: ProductType
        optional_literal: Union[Literal[1, 2, 3], None] = None

    for _ in range(10):
        model = faux(MixedModel)

        assert model.literal_field in ["a", "b", "c"]
        assert 5 <= len(model.string_field) <= 15
        assert 10 <= model.int_field <= 50
        assert 0.0 < model.float_field < 10.0
        assert isinstance(model.enum_field, ProductType)
        if model.optional_literal is not None:
            assert model.optional_literal in [1, 2, 3]
