"""
Test av ytelse for FastAPI med og uten cached_property.
"""

import time
import requests
import statistics
from typing import List

def test_api_performance(url: str, num_requests: int = 10) -> List[float]:
    """Tester API-ytelse med flere forespørsler."""
    times = []
    
    test_data = {
        "temperature": 25.0,
        "pressure": 101325.0,
        "relative_humidity": 60.0,
        "humidity_ratio": None,
        "wet_bulb": None,
        "dew_point": None
    }
    
    for i in range(num_requests):
        start_time = time.perf_counter()
        response = requests.post(url, json=test_data)
        end_time = time.perf_counter()
        
        if response.status_code == 200:
            times.append((end_time - start_time) * 1000)  # Konverter til millisekunder
        else:
            print(f"Request {i+1} failed: {response.status_code}")
    
    return times

def main():
    """Hovedfunksjon for ytelsestest."""
    api_url = "http://localhost:8000/api/v1/air-properties"
    
    print("Tester FastAPI ytelse med cached_property...")
    print("=" * 50)
    
    try:
        # Test API-ytelse
        response_times = test_api_performance(api_url, 20)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            print(f"Antall forespørsler: {len(response_times)}")
            print(f"Gjennomsnittlig responstid: {avg_time:.2f} ms")
            print(f"Minimum responstid: {min_time:.2f} ms")
            print(f"Maksimum responstid: {max_time:.2f} ms")
            print(f"Standardavvik: {std_dev:.2f} ms")
            print("-" * 30)
            print("Alle responsetider (ms):")
            for i, time_ms in enumerate(response_times, 1):
                print(f"  {i:2d}: {time_ms:.2f}")
        else:
            print("Ingen vellykkede forespørsler!")
            
    except requests.exceptions.ConnectionError:
        print("Kan ikke koble til FastAPI-serveren.")
        print("Start serveren med: python examples/fastapi_server.py")
    except Exception as e:
        print(f"Feil under testing: {e}")

if __name__ == "__main__":
    main()