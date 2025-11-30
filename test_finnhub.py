import finnhub
import time

api_key = 'd4m5dh1r01qjidhtlqs0d4m5dh1r01qjidhtlqsg'
client = finnhub.Client(api_key=api_key)

print("Testing Finnhub API...")
print(f"API Key: {api_key[:10]}...{api_key[-10:]}")

# Test 1: Quote
print("\n1. Testing quote for AAPL...")
try:
    quote = client.quote('AAPL')
    print(f"✅ Current Price: ${quote.get('c', 'N/A')}")
    print(f"   High: ${quote.get('h', 'N/A')}")
    print(f"   Low: ${quote.get('l', 'N/A')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Candles
print("\n2. Testing historical data...")
try:
    end = int(time.time())
    start = end - (30 * 24 * 60 * 60)  # 30 days ago
    res = client.stock_candles('AAPL', 'D', start, end)
    print(f"   Status: {res.get('s')}")
    if res.get('c'):
        print(f"   Data points: {len(res['c'])}")
        print(f"   Latest close: ${res['c'][-1]}")
    else:
        print(f"   No data returned")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Company Profile
print("\n3. Testing company profile...")
try:
    profile = client.company_profile2(symbol='AAPL')
    print(f"✅ Company: {profile.get('name', 'N/A')}")
    print(f"   Sector: {profile.get('finnhubIndustry', 'N/A')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ API Test Complete!")
