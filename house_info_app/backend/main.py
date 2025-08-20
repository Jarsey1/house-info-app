from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import googlemaps
import random
import json

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

@app.get("/")
async def root():
    return {"message": "House Info API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "apis": {"maps": "connected"}}

@app.post("/analyze-house")
async def analyze_house_photo(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Mock address detection (replace with Google Vision later)
        mock_addresses = [
            "123 Main Street, Beverly Hills, CA 90210",
            "456 Oak Avenue, New York, NY 10001", 
            "789 Pine Boulevard, Miami, FL 33101"
        ]
        
        best_address = random.choice(mock_addresses)
        
        # Geocode with Google Maps
        result = maps_client.geocode(best_address)
        
        if not result:
            return {"success": False, "message": "Could not geocode address"}
        
        location = result[0]['geometry']['location']
        
        # Generate property info based on location
        if "CA" in result[0]['formatted_address']:
            base_value = random.randint(800000, 2000000)
        elif "NY" in result[0]['formatted_address']:
            base_value = random.randint(600000, 1500000)
        else:
            base_value = random.randint(200000, 600000)
        
        property_info = {
            "address": {
                "address": best_address,
                "formatted_address": result[0]['formatted_address'],
                "latitude": location['lat'],
                "longitude": location['lng'],
                "place_id": result[0]['place_id']
            },
            "estimated_value": base_value,
            "property_type": "Single Family Home",
            "bedrooms": random.randint(2, 5),
            "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
            "square_feet": random.randint(1200, 3500),
            "year_built": random.randint(1950, 2020),
            "last_sale_price": int(base_value * random.uniform(0.8, 1.2))
        }
        
        return {
            "success": True,
            "message": "House information retrieved successfully (demo mode)",
            "property_info": property_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
