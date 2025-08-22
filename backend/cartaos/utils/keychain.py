"""
Secure keychain implementation for API key storage.
Uses OS-level keychain services for secure credential storage.
"""
import logging
import keyring
from typing import Optional
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SecureKeychain:
    """
    Secure keychain implementation using OS-level credential storage.
    
    Supports:
    - macOS: Keychain Access
    - Windows: Windows Credential Manager  
    - Linux: Secret Service (GNOME Keyring, KWallet)
    """
    
    def __init__(self, service_name: str = "CartaOS"):
        """
        Initialize the secure keychain.
        
        Args:
            service_name: Name of the service for keychain storage
        """
        self.service_name = service_name
        logger.info(f"Initialized SecureKeychain for service: {service_name}")
    
    def store_key(self, key_name: str, key_value: str) -> bool:
        """
        Store a key securely in the OS keychain.
        
        Args:
            key_name: Name/identifier for the key
            key_value: The secret value to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keyring.set_password(self.service_name, key_name, key_value)
            logger.info(f"Successfully stored key: {key_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to store key {key_name}: {e}")
            return False
    
    def get_key(self, key_name: str) -> Optional[str]:
        """
        Retrieve a key from the OS keychain.
        
        Args:
            key_name: Name/identifier for the key
            
        Returns:
            Optional[str]: The key value if found, None otherwise
        """
        try:
            key_value = keyring.get_password(self.service_name, key_name)
            if key_value:
                logger.info(f"Successfully retrieved key: {key_name}")
            else:
                logger.debug(f"Key not found in keychain: {key_name}")
            return key_value
        except Exception as e:
            logger.error(f"Failed to retrieve key {key_name}: {e}")
            return None
    
    def delete_key(self, key_name: str) -> bool:
        """
        Delete a key from the OS keychain.
        
        Args:
            key_name: Name/identifier for the key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keyring.delete_password(self.service_name, key_name)
            logger.info(f"Successfully deleted key: {key_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key_name}: {e}")
            return False
    
    def list_keys(self) -> list[str]:
        """
        List all keys stored for this service.
        Note: Not all keyring backends support this operation.
        
        Returns:
            list[str]: List of key names
        """
        try:
            # This is a simplified implementation
            # Real implementation would depend on keyring backend capabilities
            logger.warning("Key listing not fully supported by all keyring backends")
            return []
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []


def migrate_env_to_keychain() -> bool:
    """
    Migrate API keys from .env file to secure keychain storage.
    
    Returns:
        bool: True if migration successful, False otherwise
    """
    try:
        # Load environment variables from .env file
        from cartaos import config
        dotenv_path = config.ROOT_DIR / '.env'
        load_dotenv(dotenv_path=dotenv_path)
        
        keychain = SecureKeychain()
        migrated_keys = []
        
        # List of keys to migrate
        keys_to_migrate = [
            "GEMINI_API_KEY",
            "OBSIDIAN_VAULT_PATH"  # Also migrate vault path for consistency
        ]
        
        for key_name in keys_to_migrate:
            env_value = os.getenv(key_name)
            if env_value:
                if keychain.store_key(key_name, env_value):
                    migrated_keys.append(key_name)
                    logger.info(f"Migrated {key_name} to keychain")
                else:
                    logger.error(f"Failed to migrate {key_name} to keychain")
                    return False
        
        if migrated_keys:
            logger.info(f"Successfully migrated {len(migrated_keys)} keys to keychain")
            return True
        else:
            logger.info("No keys found in .env file to migrate")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def get_secure_api_key(key_name: str) -> Optional[str]:
    """
    Get API key with keychain-first approach and .env fallback.
    
    Args:
        key_name: Name of the API key to retrieve
        
    Returns:
        Optional[str]: The API key value if found, None otherwise
    """
    # Try keychain first
    keychain = SecureKeychain()
    key_value = keychain.get_key(key_name)
    
    if key_value:
        logger.info(f"Retrieved {key_name} from secure keychain")
        return key_value
    
    # Fallback to environment variable
    key_value = os.getenv(key_name)
    if key_value:
        logger.warning(f"Retrieved {key_name} from environment variable (consider migrating to keychain)")
        return key_value
    
    logger.error(f"API key {key_name} not found in keychain or environment")
    return None
