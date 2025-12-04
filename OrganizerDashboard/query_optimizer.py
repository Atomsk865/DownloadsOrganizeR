"""
Query Optimization & Batch Operations
Optimizes file operations with caching, connection pooling, and batch processing
"""

from functools import lru_cache
from pathlib import Path
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class QueryCache:
    """File-based query result caching with TTL"""
    
    def __init__(self):
        self.cache: Dict[str, tuple] = {}  # (result, timestamp)
        self.ttls: Dict[str, int] = {}  # TTL per query type
    
    def set_ttl(self, query_type: str, seconds: int):
        """Set TTL for query type"""
        self.ttls[query_type] = seconds
    
    def get(self, key: str, query_type: str = 'default') -> Optional[Any]:
        """Get cached result if fresh"""
        if key not in self.cache:
            return None
        
        result, timestamp = self.cache[key]
        ttl = self.ttls.get(query_type, 60)
        
        if datetime.now() - timestamp > timedelta(seconds=ttl):
            del self.cache[key]
            return None
        
        return result
    
    def set(self, key: str, result: Any):
        """Cache result"""
        self.cache[key] = (result, datetime.now())
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired = [k for k, (_, ts) in self.cache.items()
                   if now - ts > timedelta(seconds=300)]
        for k in expired:
            del self.cache[k]

class FileOperationBatcher:
    """Batch file operations to reduce I/O"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_operations: List[Dict] = []
    
    def add_read(self, path: str, operation_id: str = None):
        """Queue a file read operation"""
        self.pending_operations.append({
            'type': 'read',
            'path': path,
            'id': operation_id or path
        })
        return self._maybe_flush()
    
    def add_write(self, path: str, data: Any, operation_id: str = None):
        """Queue a file write operation"""
        self.pending_operations.append({
            'type': 'write',
            'path': path,
            'data': data,
            'id': operation_id or path
        })
        return self._maybe_flush()
    
    def add_delete(self, path: str, operation_id: str = None):
        """Queue a file delete operation"""
        self.pending_operations.append({
            'type': 'delete',
            'path': path,
            'id': operation_id or path
        })
        return self._maybe_flush()
    
    def _maybe_flush(self) -> Optional[List[Dict]]:
        """Flush if batch is full"""
        if len(self.pending_operations) >= self.batch_size:
            return self.flush()
        return None
    
    def flush(self) -> List[Dict]:
        """Execute all pending operations"""
        if not self.pending_operations:
            return []
        
        results = []
        for op in self.pending_operations:
            try:
                if op['type'] == 'read':
                    with open(op['path'], 'r') as f:
                        data = json.load(f)
                    results.append({'id': op['id'], 'success': True, 'data': data})
                
                elif op['type'] == 'write':
                    os.makedirs(os.path.dirname(op['path']), exist_ok=True)
                    with open(op['path'], 'w') as f:
                        json.dump(op['data'], f)
                    results.append({'id': op['id'], 'success': True})
                
                elif op['type'] == 'delete':
                    if os.path.exists(op['path']):
                        os.remove(op['path'])
                    results.append({'id': op['id'], 'success': True})
            
            except Exception as e:
                results.append({'id': op['id'], 'success': False, 'error': str(e)})
        
        self.pending_operations = []
        return results

class QueryOptimizer:
    """Optimizes common query patterns"""
    
    def __init__(self):
        self.cache = QueryCache()
        self.batcher = FileOperationBatcher(batch_size=100)
        
        # Set default TTLs
        self.cache.set_ttl('file_list', 30)
        self.cache.set_ttl('file_count', 60)
        self.cache.set_ttl('directory_size', 120)
        self.cache.set_ttl('statistics', 60)
    
    def count_files_in_directory(self, directory: str) -> int:
        """Count files with caching"""
        cache_key = f"count:{directory}"
        
        cached = self.cache.get(cache_key, 'file_count')
        if cached is not None:
            return cached
        
        try:
            count = sum(1 for _ in Path(directory).rglob('*') if _.is_file())
            self.cache.set(cache_key, count)
            return count
        except Exception:
            return 0
    
    def get_directory_size(self, directory: str) -> int:
        """Get directory size with caching"""
        cache_key = f"size:{directory}"
        
        cached = self.cache.get(cache_key, 'directory_size')
        if cached is not None:
            return cached
        
        try:
            total = sum(f.stat().st_size for f in Path(directory).rglob('*') if f.is_file())
            self.cache.set(cache_key, total)
            return total
        except Exception:
            return 0
    
    def list_files_batch(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """List files with filtering and caching"""
        cache_key = f"list:{directory}:{','.join(extensions or [])}"
        
        cached = self.cache.get(cache_key, 'file_list')
        if cached is not None:
            return cached
        
        try:
            results = []
            for file_path in Path(directory).rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Filter by extension if specified
                if extensions and file_path.suffix.lower() not in [f".{e.lower()}" for e in extensions]:
                    continue
                
                results.append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                })
            
            self.cache.set(cache_key, results)
            return results
        except Exception:
            return []
    
    def get_file_hashes_batch(self, file_paths: List[str]) -> Dict[str, str]:
        """Get hashes for multiple files efficiently"""
        import hashlib
        
        results = {}
        
        # Use batch processing for I/O
        for path in file_paths:
            try:
                with open(path, 'rb') as f:
                    file_hash = hashlib.sha256()
                    # Read in 64KB chunks for memory efficiency
                    for chunk in iter(lambda: f.read(65536), b''):
                        file_hash.update(chunk)
                    results[path] = file_hash.hexdigest()
            except Exception as e:
                results[path] = f"error:{str(e)}"
        
        return results
    
    def bulk_update_statistics(self, updates: List[Dict]) -> List[Dict]:
        """Batch update statistics"""
        for update in updates:
            self.batcher.add_write(
                update['path'],
                update['data'],
                operation_id=update.get('id')
            )
        
        return self.batcher.flush()
    
    def clear_cache(self):
        """Clear expired cache entries"""
        self.cache.clear_expired()

# Global optimizer instance
query_optimizer = QueryOptimizer()

def get_optimizer() -> QueryOptimizer:
    """Get global query optimizer"""
    return query_optimizer

# Common optimized queries
@lru_cache(maxsize=128)
def get_file_extension(filename: str) -> str:
    """Get file extension (cached)"""
    return Path(filename).suffix.lower()

def get_file_category(filename: str) -> Optional[str]:
    """Get category for file (uses cached extension)"""
    ext = get_file_extension(filename)
    
    # Common category mappings
    categories = {
        '.jpg': 'Images',
        '.jpeg': 'Images',
        '.png': 'Images',
        '.gif': 'Images',
        '.pdf': 'Documents',
        '.doc': 'Documents',
        '.docx': 'Documents',
        '.xls': 'Documents',
        '.xlsx': 'Documents',
        '.mp4': 'Videos',
        '.avi': 'Videos',
        '.mov': 'Videos',
        '.zip': 'Archives',
        '.rar': 'Archives',
        '.7z': 'Archives',
    }
    
    return categories.get(ext)

def batch_categorize_files(files: List[str]) -> Dict[str, str]:
    """Categorize multiple files efficiently"""
    results = {}
    for file in files:
        category = get_file_category(file)
        results[file] = category or 'Other'
    return results
