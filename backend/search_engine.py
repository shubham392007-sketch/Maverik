import os
import sqlite3
import threading
import time
from database import get_db_connection

class SearchEngine:
    def __init__(self):
        self.is_indexing = False
        self.last_index_time = 0

    def start_background_indexer(self):
        """Starts the indexing process in a background thread."""
        if not self.is_indexing:
            thread = threading.Thread(target=self._index_files_routine, daemon=True)
            thread.start()

    def _index_files_routine(self):
        self.is_indexing = True
        try:
            # We index both C and D drives as requested
            search_roots = ["C:\\", "D:\\"]

            print(f"[Indexer] Starting scan of {search_roots}...")
            start_time = time.time()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Use a fast batch insert strategy
            batch = []
            batch_size = 1000
            total_indexed = 0
            
            # Common directories to skip to speed up scanning
            skip_dirs = {'.git', 'node_modules', 'venv', '.env', '__pycache__', 'AppData',
                         'Windows', '$Recycle.Bin', 'System Volume Information', 'ProgramData',
                         'Recovery', 'PerfLogs'}
            
            for base_path in search_roots:
                try:
                    for root, dirs, files in os.walk(base_path, onerror=lambda e: None):
                        # Modify dirs in-place to skip hidden/heavy folders
                        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                    
                        # Index directories
                        for d in dirs:
                            path = os.path.join(root, d)
                            try:
                                stat = os.stat(path)
                                batch.append((d, path, '', 0, stat.st_mtime, True))
                            except Exception:
                                pass
                    
                        # Index files
                        for f in files:
                            path = os.path.join(root, f)
                            try:
                                stat = os.stat(path)
                                ext = os.path.splitext(f)[1].lower()
                                batch.append((f, path, ext, stat.st_size, stat.st_mtime, False))
                            except Exception:
                                pass

                        if len(batch) >= batch_size:
                            cursor.executemany('''
                                INSERT OR REPLACE INTO file_index 
                                (filename, path, extension, size_bytes, modified_timestamp, is_folder)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', batch)
                            conn.commit()
                            total_indexed += len(batch)
                            batch.clear()
                except Exception as walk_err:
                    print(f"[Indexer] Error walking {base_path}: {walk_err}")
            
            # Insert any remaining records
            if batch:
                cursor.executemany('''
                    INSERT OR REPLACE INTO file_index 
                    (filename, path, extension, size_bytes, modified_timestamp, is_folder)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', batch)
                conn.commit()
                total_indexed += len(batch)
            
            conn.close()
            end_time = time.time()
            print(f"[Indexer] Finished scanning in {end_time - start_time:.2f} seconds. Indexed {total_indexed} items.")
            self.last_index_time = time.time()
        except Exception as e:
            print(f"[Indexer] Error: {e}")
        finally:
            self.is_indexing = False

    def search(self, query: str = "", extension: str = None, min_size: int = None, limit: int = 50):
        """Searches the local index."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT filename, path, extension, size_bytes, modified_timestamp, is_folder FROM file_index WHERE 1=1"
        params = []
        
        if query:
            sql += " AND filename LIKE ?"
            params.append(f"%{query}%")
            
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            sql += " AND extension = ?"
            params.append(extension.lower())
            
        if min_size is not None:
            sql += " AND size_bytes >= ?"
            params.append(min_size)
            
        # Prioritize files with shorter paths (usually more relevant) and matching names
        sql += " ORDER BY is_folder DESC, LENGTH(path) ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "filename": row["filename"],
                "path": row["path"],
                "extension": row["extension"],
                "size_bytes": row["size_bytes"],
                "modified_timestamp": row["modified_timestamp"],
                "is_folder": bool(row["is_folder"])
            })
        return results

    def get_recent_files(self, limit: int = 10):
        """Fetches files that were recently opened via the app."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.filename, f.path, f.extension, f.size_bytes, f.modified_timestamp, f.is_folder, s.last_opened
            FROM file_stats s
            JOIN file_index f ON s.path = f.path
            ORDER BY s.last_opened DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "filename": row["filename"],
                "path": row["path"],
                "extension": row["extension"],
                "size_bytes": row["size_bytes"],
                "modified_timestamp": row["modified_timestamp"],
                "is_folder": bool(row["is_folder"]),
                "last_opened": row["last_opened"]
            })
        return results

    def track_file_open(self, path: str):
        """Records when a file is opened for 'Recent' tracking."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_stats (path, open_count, last_opened)
            VALUES (?, 1, ?)
            ON CONFLICT(path) DO UPDATE SET 
                open_count = open_count + 1,
                last_opened = excluded.last_opened
        ''', (path, time.time()))
        conn.commit()
        conn.close()

# Global singleton
search_engine = SearchEngine()
