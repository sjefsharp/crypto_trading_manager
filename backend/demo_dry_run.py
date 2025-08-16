"""
Demonstratie script voor dry-run functionaliteit
Test hoe de trading mode API en simulatie werkt
"""

import json

import requests

# Base URL voor de API (lokaal)
BASE_URL = "http://localhost:8000"


def test_trading_mode_api():
    """Test de trading mode API endpoints"""
    print("=== TRADING MODE API DEMONSTRATIE ===\n")

    # 1. Check huidige status
    print("1. Huidige trading mode status:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/trading-mode/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Mode: {status['current_mode']}")
            print(f"   Dry Run: {status['dry_run_enabled']}")
            print(f"   Live Trading: {status['is_live_trading']}")
            print(f"   Warning: {status['warning_message']}")
        else:
            print(f"   Fout: {response.status_code}")
    except Exception as e:
        print(f"   Fout bij status check: {e}")

    print("\n" + "=" * 50)

    # 2. Test mode wisselen naar demo
    print("\n2. Wisselen naar DEMO mode:")
    try:
        data = {"mode": "demo", "force_dry_run": False}
        response = requests.post(f"{BASE_URL}/api/v1/trading-mode/set", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"   Nieuwe mode: {result['current_mode']}")
            print(f"   Dry Run: {result['dry_run_enabled']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"   Fout: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Fout bij mode switch: {e}")

    print("\n" + "=" * 50)

    # 3. Test live trading validatie
    print("\n3. Live trading validatie:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/trading-mode/validate-live")
        if response.status_code == 200:
            validation = response.json()
            print(f"   Kan live traden: {validation['can_trade_live']}")
            print(f"   Requirements: {validation['requirements']}")
            print(f"   Huidige mode: {validation['current_mode']}")
        else:
            print(f"   Fout: {response.status_code}")
    except Exception as e:
        print(f"   Fout bij validatie: {e}")

    print("\n" + "=" * 50)

    # 4. Test emergency dry-run enable
    print("\n4. Emergency dry-run enable:")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/trading-mode/enable-dry-run")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result['dry_run_enabled']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"   Fout: {response.status_code}")
    except Exception as e:
        print(f"   Fout bij emergency enable: {e}")

    print("\n" + "=" * 50)


def test_order_simulation():
    """Test order simulatie in dry-run mode"""
    print("\n5. Order simulatie test:")
    try:
        # Eerst zorgen dat we in dry-run mode zijn
        requests.post(
            f"{BASE_URL}/api/v1/trading-mode/set",
            json={"mode": "dry_run", "force_dry_run": True},
        )

        # Test een order plaatsen
        order_data = {
            "market": "BTC-EUR",
            "side": "buy",
            "order_type": "market",
            "amount": 0.001,
        }

        # Hier zouden we een order endpoint kunnen testen als die er is
        print(f"   Order data: {json.dumps(order_data, indent=2)}")
        print("   (In dry-run mode zou dit een gesimuleerde response geven)")

    except Exception as e:
        print(f"   Fout bij order simulatie: {e}")


def test_health_check():
    """Test health check met trading mode info"""
    print("\n6. Health check met trading mode:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   Status: {health['status']}")
            print(f"   Trading Mode: {health.get('trading_mode', 'Not available')}")
            print(f"   Mode Warning: {health.get('mode_warning', 'Not available')}")
        else:
            print(f"   Fout: {response.status_code}")
    except Exception as e:
        print(f"   Fout bij health check: {e}")


if __name__ == "__main__":
    print("Starting Trading Mode Demonstratie...")
    print("Zorg dat de server draait met: uvicorn app.main:app --reload")
    print()

    test_trading_mode_api()
    test_order_simulation()
    test_health_check()

    print("\n" + "=" * 50)
    print("Demonstratie voltooid!")
    print("\nKenmerken van het dry-run systeem:")
    print("- Standaard in DRY_RUN mode voor veiligheid")
    print("- DEMO mode voor realistische simulatie")
    print("- LIVE mode alleen met API credentials en expliciete bevestiging")
    print("- Emergency dry-run enable voor directe veiligheid")
    print("- Simulatie van orders en balances in non-live modes")
    print("- Waarschuwingen en validaties voor live trading")
