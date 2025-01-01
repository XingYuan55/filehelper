import json
import os

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("配置文件不存在，使用默认配置")
            self.config = {
                "network": {
                    "port": 9999,
                    "host": "0.0.0.0",
                    "buffer_size": 1024,
                    "timeout": 1.0
                },
                "file": {
                    "max_size": 4294967296,  # 4GB
                    "max_size_human": "4GB",
                    "allowed_extensions": ["*"],
                    "save_path": "./received_files"
                },
                "transfer": {
                    "compress_level": 6,
                    "show_progress": True
                }
            }
            self._save_config()
    
    def _save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get(self, section, key):
        return self.config.get(section, {}).get(key)
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config() 