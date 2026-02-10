import os
import sys
import json
import hashlib
import platform
from pathlib import Path
from typing import Dict, Tuple, Optional

class FolderLockCore:
    def __init__(self):
        self.system = platform.system()
        self.config_dir = Path.home() / '.folder_lock'
        self.config_file = self.config_dir / 'locks.json'
        self.config_dir.mkdir(exist_ok=True)
        self.data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load locked folders database and master key"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Handle legacy format where root was just locks
                    if 'locks' not in data and 'master_key_hash' not in data:
                        # Assume it's the old format which was just the locks dict
                        # But check if it's empty or looks like locks dict
                        return {'locks': data, 'master_key_hash': None}
                    return data
            except:
                return {'locks': {}, 'master_key_hash': None}
        return {'locks': {}, 'master_key_hash': None}
    
    def _save_data(self):
        """Save locked folders database"""
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    @property
    def locks(self) -> Dict:
        return self.data.get('locks', {})
        
    @property
    def master_key_hash(self) -> Optional[str]:
        return self.data.get('master_key_hash')

    def set_master_key(self, password: str):
        """Set or update the master key"""
        self.data['master_key_hash'] = self._hash_password(password)
        self._save_data()
        
    def verify_master_key(self, password: str) -> bool:
        """Verify if the provided password matches the master key"""
        if not self.master_key_hash:
            return False
        return self._hash_password(password) == self.master_key_hash
    
    def _hash_password(self, password: str) -> str:
        """Create secure hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _set_permissions_windows(self, folder_path: Path, lock: bool):
        """Set folder permissions on Windows using icacls"""
        try:
            path_str = str(folder_path.absolute())
            
            if lock:
                # Remove all permissions except for system and admin
                # Deny read, write, and execute for current user
                os.system(f'icacls "{path_str}" /deny %USERNAME%:(OI)(CI)F /T >nul 2>&1')
                os.system(f'icacls "{path_str}" /inheritance:r >nul 2>&1')
            else:
                # Restore full permissions
                os.system(f'icacls "{path_str}" /grant %USERNAME%:(OI)(CI)F /T >nul 2>&1')
                os.system(f'icacls "{path_str}" /inheritance:e >nul 2>&1')
            
            return True
        except Exception as e:
            # print(f"Error setting permissions: {e}")
            return False
    
    def _set_permissions_unix(self, folder_path: Path, lock: bool):
        """Set folder permissions on Linux/Unix systems"""
        try:
            if lock:
                # Remove all permissions (000)
                os.chmod(folder_path, 0o000)
                # Also lock all contents
                for item in folder_path.rglob('*'):
                    try:
                        os.chmod(item, 0o000)
                    except:
                        pass
            else:
                # Restore read, write, execute permissions (755)
                os.chmod(folder_path, 0o755)
                # Restore permissions for contents
                for item in folder_path.rglob('*'):
                    try:
                        if item.is_dir():
                            os.chmod(item, 0o755)
                        else:
                            os.chmod(item, 0o644)
                    except:
                        pass
            
            return True
        except Exception as e:
            return False
    
    def lock_folder(self, folder_path: str, password: str) -> Tuple[bool, str]:
        """Lock a folder with password protection"""
        path = Path(folder_path).resolve()
        
        if not path.exists():
            return False, "Folder does not exist"
        
        if not path.is_dir():
            return False, "Path is not a folder"
        
        path_str = str(path)
        
        if path_str in self.locks:
            return False, "Folder is already locked"
        
        # Set OS permissions
        if self.system == "Windows":
            success = self._set_permissions_windows(path, lock=True)
        else:
            success = self._set_permissions_unix(path, lock=True)
        
        if not success:
            return False, "Failed to set OS permissions"
        
        # Store password hash
        if 'locks' not in self.data:
            self.data['locks'] = {}
            
        self.data['locks'][path_str] = {
            'password_hash': self._hash_password(password),
            'original_path': str(path),
            'system': self.system,
            'name': path.name
        }
        self._save_data()
        
        return True, "Folder locked successfully"
    
    def unlock_folder(self, folder_path: str, password: str) -> Tuple[bool, str]:
        """Unlock a folder with password verification (supports master key)"""
        path = Path(folder_path).resolve()
        path_str = str(path)
        
        if path_str not in self.locks:
            return False, "Folder is not locked or not found in database"
        
        # Verify password
        password_hash = self._hash_password(password)
        is_correct_password = password_hash == self.locks[path_str]['password_hash']
        is_master_key = self.verify_master_key(password)
        
        if not is_correct_password and not is_master_key:
            return False, "Invalid password"
        
        # Restore OS permissions
        if self.system == "Windows":
            success = self._set_permissions_windows(path, lock=False)
        else:
            success = self._set_permissions_unix(path, lock=False)
        
        if not success:
            return False, "Failed to restore permissions"
        
        # Remove from database
        del self.data['locks'][path_str]
        self._save_data()
        
        return True, "Folder unlocked successfully"
    
    def get_all_locks(self) -> Dict:
        return self.locks.copy()
