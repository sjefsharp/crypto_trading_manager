"""
Secure configuration management for API keys and sensitive data
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet


class SecureConfig:
    """Secure configuration manager for API keys and sensitive data"""

    def __init__(self, config_dir: str = None):
        """Initialize secure configuration manager"""
        if config_dir is None:
            self.config_dir = Path.home() / ".crypto_trading_manager"
        else:
            self.config_dir = Path(config_dir)

        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.enc"
        self.key_file = self.config_dir / ".key"

        # Initialize or load encryption key
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption system"""
        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            # Generate new key
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
            # Make key file readable only by owner
            os.chmod(self.key_file, 0o600)

        self.cipher = Fernet(self.key)

    def set_api_keys(self, bitvavo_key: str, bitvavo_secret: str):
        """Securely store API keys"""
        config_data = {
            "bitvavo": {"api_key": bitvavo_key, "api_secret": bitvavo_secret}
        }

        # Encrypt and store
        encrypted_data = self.cipher.encrypt(json.dumps(config_data).encode())
        with open(self.config_file, "wb") as f:
            f.write(encrypted_data)

        # Make config file readable only by owner
        os.chmod(self.config_file, 0o600)

        print("✅ API keys stored securely")

    def get_api_keys(self) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt API keys"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"❌ Error reading API keys: {e}")
            return None

    def get_bitvavo_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Get Bitvavo API credentials"""
        config = self.get_api_keys()
        if config and "bitvavo" in config:
            bitvavo_config = config["bitvavo"]
            return bitvavo_config.get("api_key"), bitvavo_config.get("api_secret")
        return None, None

    def delete_config(self):
        """Delete all stored configuration"""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.key_file.exists():
            self.key_file.unlink()
        print("🗑️ Configuration deleted")

    def config_exists(self) -> bool:
        """Check if configuration exists"""
        return self.config_file.exists()

    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration and return status"""
        config = self.get_api_keys()
        if not config:
            return {"valid": False, "bitvavo": False}

        bitvavo_valid = (
            "bitvavo" in config
            and config["bitvavo"].get("api_key")
            and config["bitvavo"].get("api_secret")
        )

        return {"valid": bitvavo_valid, "bitvavo": bitvavo_valid}  # Bitvavo is required


# Global config instance
_config = None


def get_secure_config() -> SecureConfig:
    """Get global secure configuration instance"""
    global _config
    if _config is None:
        _config = SecureConfig()

    return _config


def setup_initial_config():
    """Interactive setup for initial configuration"""
    print("🔧 Crypto Trading Manager - Initial Configuration")
    print("=" * 50)
    print("This will securely store your API keys for trading operations.")
    print("API keys are encrypted and stored in your home directory.")
    print()

    config = get_secure_config()

    # Check if config already exists
    if config.config_exists():
        overwrite = input("Configuration already exists. Overwrite? (y/N): ").lower()
        if overwrite != "y":
            print("Configuration setup cancelled.")
            return

    print("📋 Please provide your API credentials:")
    print()

    # Bitvavo credentials (required)
    print("🔹 Bitvavo API (Required for trading)")
    bitvavo_key = input("Bitvavo API Key: ").strip()
    bitvavo_secret = input("Bitvavo API Secret: ").strip()

    if not bitvavo_key or not bitvavo_secret:
        print("❌ Bitvavo credentials are required!")
        return

    # Store configuration
    config.set_api_keys(bitvavo_key=bitvavo_key, bitvavo_secret=bitvavo_secret)

    # Validate configuration
    validation = config.validate_config()
    print("\n📊 Configuration Status:")
    print(f"✅ Bitvavo: {'✓' if validation['bitvavo'] else '✗'}")

    if validation["valid"]:
        print("\n🎉 Configuration completed successfully!")
        print("Your API keys are securely encrypted and stored.")
    else:
        print("\n⚠️ Configuration incomplete. Please check your credentials.")


if __name__ == "__main__":
    setup_initial_config()
