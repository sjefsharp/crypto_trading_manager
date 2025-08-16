#!/usr/bin/env python3
"""
Configuration setup script for Crypto Trading Manager
Run this script to securely configure your API keys
"""
import sys
from pathlib import Path

from app.config.secure_config import get_secure_config, setup_initial_config

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def main():
    """Main configuration function"""
    print("🔐 Crypto Trading Manager - Secure Configuration Setup")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            setup_initial_config()
        elif command == "status":
            show_config_status()
        elif command == "delete":
            delete_config()
        elif command == "test":
            test_api_connection()
        else:
            show_help()
    else:
        show_help()


def show_config_status():
    """Show current configuration status"""
    config = get_secure_config()

    print("📊 Configuration Status:")
    print("-" * 30)

    if not config.config_exists():
        print("❌ No configuration found")
        print("Run: python configure.py setup")
        return

    validation = config.validate_config()

    print(
        f"✅ Configuration file: {'Found' if config.config_exists() else 'Not found'}"
    )
    print(f"🔑 Bitvavo API: {'✓ Configured' if validation['bitvavo'] else '✗ Missing'}")
    print(
        f"📈 FRED API: {'✓ Configured' if validation['fred'] else '✗ Not configured (optional)'}"
    )
    print(
        f"📊 BLS API: {'✓ Configured' if validation['bls'] else '✗ Not configured (optional)'}"
    )
    print(
        f"🎯 Overall Status: {'✅ Ready' if validation['valid'] else '⚠️ Needs attention'}"
    )


def delete_config():
    """Delete configuration"""
    config = get_secure_config()

    if not config.config_exists():
        print("❌ No configuration found to delete")
        return

    confirm = input(
        "⚠️ This will permanently delete your API configuration. Continue? (y/N): "
    )
    if confirm.lower() == "y":
        config.delete_config()
        print("✅ Configuration deleted successfully")
    else:
        print("❌ Operation cancelled")


def test_api_connection():
    """Test API connection"""
    import asyncio

    from app.services.bitvavo_api_secure import BitvavoAPI

    async def run_test():
        print("🔗 Testing API connection...")

        api = BitvavoAPI()
        result = await api.test_connection()

        if result["status"] == "success":
            print("✅ API connection successful!")
            print(f"🕒 Server time: {result.get('server_time', 'N/A')}")
        else:
            print(f"❌ API connection failed: {result['message']}")
            if not result["authenticated"]:
                print("💡 Tip: Run 'python configure.py setup' to configure API keys")

    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"❌ Test failed: {e}")


def show_help():
    """Show help information"""
    print("🔧 Crypto Trading Manager Configuration Tool")
    print()
    print("Commands:")
    print("  setup    - Interactive setup of API keys")
    print("  status   - Show current configuration status")
    print("  test     - Test API connection")
    print("  delete   - Delete stored configuration")
    print()
    print("Examples:")
    print("  python configure.py setup    # Set up API keys")
    print("  python configure.py status   # Check configuration")
    print("  python configure.py test     # Test API connection")
    print()
    print("Security Notes:")
    print("• API keys are encrypted and stored in ~/.crypto_trading_manager/")
    print("• Only the current user can read the configuration files")
    print("• Keys are never stored in source code or version control")


if __name__ == "__main__":
    main()
