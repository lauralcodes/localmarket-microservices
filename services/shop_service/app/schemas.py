from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from datetime import datetime



class ShopCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None

    email: EmailStr # validates email addresses
    phone: str | None = Field(default=None, max_length=30)
    website: HttpUrl | None = None # validates website and image URLs

    street_address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)

    logo_url: HttpUrl | None = None
    cover_image_url: HttpUrl | None = None


class ShopUpdate(BaseModel): # This makes fields optional so a user can update only the city, for example, without sending the entire shop profile.
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None

    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    website: HttpUrl | None = None

    street_address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)

    logo_url: HttpUrl | None = None
    cover_image_url: HttpUrl | None = None


class ShopResponse(BaseModel): # Defines the information returned by the API.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    email: EmailStr
    phone: str | None
    website: str | None

    street_address: str | None
    city: str | None
    postal_code: str | None
    country: str | None

    logo_url: str | None
    cover_image_url: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    