from pydantic import BaseModel, Field

from fauxdantic import faux


class BasicLocation(BaseModel):
    city: str
    state: str
    country: str


class DetailedAddress(BaseModel):
    street_address: str
    city: str
    state_province: str
    country: str
    zip_code: str


class ConstrainedGeographic(BaseModel):
    city_name: str = Field(..., max_length=20)
    state_abbr: str = Field(..., max_length=3)
    state_full: str = Field(..., max_length=50)
    province: str = Field(..., max_length=30)
    region_name: str = Field(..., max_length=25)
    country_code: str = Field(..., max_length=3)
    country_full: str = Field(..., max_length=50)


def test_basic_geographic_fields():
    """Test that basic geographic fields generate appropriate values"""
    for _ in range(10):  # Test multiple times for consistency
        location = faux(BasicLocation)

        # Verify types
        assert isinstance(location.city, str)
        assert isinstance(location.state, str)
        assert isinstance(location.country, str)

        # Verify non-empty
        assert len(location.city) > 0
        assert len(location.state) > 0
        assert len(location.country) > 0


def test_state_province_variations():
    """Test that different state/province field names are detected"""
    for _ in range(5):
        address = faux(DetailedAddress)

        # state_province should be detected as a geographic field
        assert isinstance(address.state_province, str)
        assert len(address.state_province) > 0


def test_constrained_geographic_fields():
    """Test that geographic fields respect length constraints"""
    for _ in range(10):
        geo = faux(ConstrainedGeographic)

        # Test length constraints
        assert len(geo.city_name) <= 20
        assert len(geo.state_abbr) <= 3
        assert len(geo.state_full) <= 50
        assert len(geo.province) <= 30
        assert len(geo.region_name) <= 25
        assert len(geo.country_code) <= 3
        assert len(geo.country_full) <= 50

        # State abbreviation should be short when constrained
        assert len(geo.state_abbr) >= 2  # Standard state abbreviations are 2 chars

        # Country code should be short when constrained
        assert len(geo.country_code) >= 2  # Standard country codes are 2-3 chars


def test_geographic_field_realism():
    """Test that generated geographic data looks realistic"""
    location = faux(BasicLocation)

    # Cities should not contain obvious fake patterns
    assert not location.city.startswith("fake")
    assert not location.city.startswith("test")

    # State should be a reasonable length (US states are typically 4-20 chars)
    assert 2 <= len(location.state) <= 25

    # Country should be a reasonable length
    assert 3 <= len(location.country) <= 50


def test_very_short_constraints():
    """Test behavior with very short length constraints"""

    class VeryShortGeo(BaseModel):
        state_code: str = Field(..., max_length=2)
        country_code: str = Field(..., max_length=2)

    for _ in range(5):
        geo = faux(VeryShortGeo)

        # Should handle very short constraints gracefully
        assert len(geo.state_code) <= 2
        assert len(geo.country_code) <= 2
        assert len(geo.state_code) > 0
        assert len(geo.country_code) > 0


def test_mixed_geographic_and_other_fields():
    """Test geographic fields work well with other field types"""

    class Organization(BaseModel):
        name: str
        headquarters_city: str
        operating_state: str
        founding_country: str
        employee_count: int
        description: str
        website_url: str

    org = faux(Organization)

    # Geographic fields
    assert isinstance(org.headquarters_city, str)
    assert isinstance(org.operating_state, str)
    assert isinstance(org.founding_country, str)

    # Other fields should still work
    assert isinstance(org.name, str)
    assert isinstance(org.employee_count, int)
    assert isinstance(org.description, str)
    assert isinstance(org.website_url, str)

    # Geographic fields should be reasonable
    assert len(org.headquarters_city) > 0
    assert len(org.operating_state) > 0
    assert len(org.founding_country) > 0
