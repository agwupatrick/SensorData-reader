# sensor_reader.py
import serial
import uuid
import json
import httpx
import asyncio

FASTAPI_URL = "https://esmarthomeapi.onrender.com/sensor/"

class SensorReader:
    def __init__(self, comport, baudrate):
        self.comport = comport
        self.baudrate = baudrate
        self.ser = serial.Serial(comport, baudrate, timeout=0.1)
    
    async def read_serial(self):
        buffer = ""
        while True:
            try:
                # Read data from serial
                buffer += self.ser.readline().decode().strip()
                # Try to parse the data as JSON if we have a complete line
                if buffer:
                    try:
                        parsed_data = json.loads(buffer)
                        print(f'Received data: {parsed_data}')
                        # Store parsed data and clear buffer
                        await self.store_data(parsed_data)
                        buffer = ""  # Reset buffer after successful parsing
                    except json.JSONDecodeError:
                        # Incomplete or invalid JSON, skip this iteration
                        print(f"Incomplete or invalid data, buffering: {buffer}")
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break  # Exit if an error occurs

    async def store_data(self, parsed_data):
        async with httpx.AsyncClient() as client:
            # Ensure valid UUID for device_id
            device_id = "d484db62-5506-496d-b70c-f6a2d1f3eb7c"
            try:
                device_id = uuid.UUID(device_id)
            except ValueError:
                print(f"Invalid UUID format for device_id: {device_id}")
                return
            
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

async def main():
    comport = 'COM8'  # Replace with the correct port
    baudrate = 9600  # Replace with the correct baud rate
    sensor_reader = SensorReader(comport, baudrate)
    await sensor_reader.read_serial()

if __name__ == "__main__":
    asyncio.run(main())
