import json
import os
import time
from typing import Dict, Any, Optional

from ..types import VerificationResult

class VerificationCacheOptions:
    def __init__(self, ttl_ms: int = 300_000, max_entries: int = 1000, persist_path: Optional[str] = None):
        self.ttl_ms = ttl_ms
        self.max_entries = max_entries
        self.persist_path = persist_path

class VerificationCache:
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        if options is None:
            options = {}
        self.ttl_ms = options.get('ttlMs', 300_000)
        self.max_entries = options.get('maxEntries', 1000)
        self.persist_path = options.get('persistPath')
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        if self.persist_path:
            self._load_from_disk()

    def get(self, hash_str: str) -> Optional[VerificationResult]:
        entry = self.cache.get(hash_str)
        if not entry:
            return None
            
        now = int(time.time() * 1000)
        if now - entry['cachedAt'] > entry['ttlMs']:
            del self.cache[hash_str]
            return None
            
        result = dict(entry['result'])
        result['fromCache'] = True
        result['cachedTimestamp'] = entry['cachedAt']
        return result

    def set(self, hash_str: str, result: VerificationResult) -> None:
        if len(self.cache) >= self.max_entries and hash_str not in self.cache:
            # Basic LRU
            oldest_hash = None
            oldest_time = float('inf')
            
            for h, entry in self.cache.items():
                if entry['cachedAt'] < oldest_time:
                    oldest_time = entry['cachedAt']
                    oldest_hash = h
                    
            if oldest_hash:
                del self.cache[oldest_hash]

        self.cache[hash_str] = {
            'result': result,
            'cachedAt': int(time.time() * 1000),
            'ttlMs': self.ttl_ms
        }

        if self.persist_path:
            self._save_to_disk()

    def invalidate(self, hash_str: str) -> None:
        if hash_str in self.cache:
            del self.cache[hash_str]
        if self.persist_path:
            self._save_to_disk()

    def clear(self) -> None:
        self.cache.clear()
        if self.persist_path:
            self._save_to_disk()

    def _load_from_disk(self) -> None:
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache = data
        except Exception:
            pass

    def _save_to_disk(self) -> None:
        if not self.persist_path:
            return
        try:
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
