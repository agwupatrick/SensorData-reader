# sensor_reader.py
import serial
import uuid
import json
import httpx
import asyncio

# Replace `your_fastapi_url` with the actual endpoint URL for your FastAPI app
FASTAPI_URL = "http://localhost:8000/sensor/"

class SensorReader:
    @classmethod
    def read_serial(cls, comport, baudrate):
        ser = serial.Serial(comport, baudrate, timeout=0.1)
        while True:
            data = ser.readline().decode().strip()
            if data:
                try:
                    # Parse JSON data
                    parsed_data = json.loads(data)
                    print(f'Received data: {parsed_data}')
                    # Call the async store_data function
                    asyncio.run(cls.store_data(parsed_data))
                except json.JSONDecodeError:
                    print(f"Invalid data format: {data}")

    @staticmethod
    async def store_data(parsed_data):
        async with httpx.AsyncClient() as client:
            # Convert device_id to a UUID if necessary
            device_id = "d484db62-5506-496d-b70c-f6a2d1f3eb7c"  # Replace with actual device ID
            try:
                device_id = uuid.UUID(device_id)
            except ValueError:
                print(f"Invalid UUID format for device_id: {device_id}")
                return
            
            # Extract sensor data from the parsed JSON
            sensor_data = {
                "device_id": str(device_id),
                "mq5_level": parsed_data.get("gas_value"),
                "motion_status": parsed_data.get("motion_detected"),
                "temperature": parsed_data.get("temperature_dht"),
                "humidity": parsed_data.get("humidity")
            }

            try:
                response = await client.post(FASTAPI_URL, json=sensor_data)
                if response.status_code == 201:
                    print("Data stored successfully.")
                else:
                    print(f"Failed to store data: {response.status_code}, {response.text}")
            except httpx.HTTPError as e:
                print(f"HTTP error occurred: {e}")

def start_sensor_reading():
    comport = 'COM8'  # Replace with the correct port
    baudrate = 9600  # Replace with the correct baud rate
    SensorReader.read_serial(comport, baudrate)

if __name__ == "__main__":
    start_sensor_reading()
