from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import googlemaps
import random

app = FastAPI(title="House Info API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAPS_API_KEY = "AIzaSyBxq17PjCIHboeslPAeS2jBT1-IAOpKAEs"
maps_client = googlemaps.Client(key=MAPS_API_KEY)

class AddressResult(BaseModel):
    address: str
    formatted_address: str
    latitude: float
    longitude: float
    place_id: str

class PropertyInfo(BaseModel):
    address: AddressResult
    estimated_value: Optional[int] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    year_built: Optional[int] = None
    last_sale_price: Optional[int] = None

class HouseInfoResponse(BaseModel):
    success: bool
    message: str
    property_info: Optional[PropertyInfo] = None

@app.get("/")
async def root():
    return {"message": "House Info API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "apis": {"maps": "connected"}}

@app.post("/analyze-house", response_model=HouseInfoResponse)
async def analyze_house_photo(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # For now, simulate address detection with mock data
        # In production, this would use Google Vision API
        mock_addresses = [
            "123 Main Street, Beverly Hills, CA 90210",
            "456 Oak Avenue, New York, NY 10001", 
            "789 Pine Boulevard, Miami, FL 33101"
        ]
        
        best_address = random.choice(mock_addresses)
        
        # Geocode the address
        result = maps_client.geocode(best_address)
        
        if not result:
            return HouseInfoResponse(success=False, message="Could not geocode address")
        
        location = result[0]['geometry']['location']
        address_result = AddressResult(
            address=best_address,
            formatted_address=result[0]['formatted_address'],
            latitude=location['lat'],
            longitude=location['lng'],
            place_id=result[0]['place_id']
        )
        
        # Generate mock property info based on location
        if "CA" in address_result.formatted_address:
            base_value = random.randint(800000, 2000000)
        elif "NY" in address_result.formatted_address:
            base_value = random.randint(600000, 1500000)
        else:
            base_value = random.randint(200000, 600000)
        
        property_info = PropertyInfo(
            address=address_result,
            estimated_value=base_value,
            property_type="Single Family Home",
            bedrooms=random.randint(2, 5),
            bathrooms=random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
            square_feet=random.randint(1200, 3500),
            year_built=random.randint(1950, 2020),
            last_sale_price=int(base_value * random.uniform(0.8, 1.2))
        )
        
        return HouseInfoResponse(
            success=True,
            message="House information retrieved successfully (demo mode)",
            property_info=property_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
