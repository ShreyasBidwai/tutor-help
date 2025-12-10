# SQLite Concurrency Optimizations

## Overview
This document describes the SQLite optimizations implemented to improve concurrent user handling without changing the database system or requiring additional dependencies.

## Changes Applied

### 1. WAL Mode (Write-Ahead Logging)
- **Status**: ✅ Enabled
- **Location**: `database.py` - `get_db_connection()`
- **Benefit**: 
  - Allows multiple concurrent readers
  - One writer at a time (but much better than default mode)
  - Readers don't block writers
  - Writers don't block readers (as much)

### 2. Connection Timeout
- **Status**: ✅ Enabled (20 seconds default)
- **Benefit**: Handles "database is locked" errors gracefully

### 3. Performance PRAGMA Settings
- **synchronous=NORMAL**: Faster than FULL, still safe
- **cache_size=-64000**: 64MB cache for faster queries
- **temp_store=MEMORY**: Store temporary tables in RAM
- **mmap_size=268435456**: 256MB memory-mapped I/O
- **foreign_keys=ON**: Ensure referential integrity

### 4. Retry Logic Helper
- **Status**: ✅ Added `execute_with_retry()` function
- **Benefit**: Automatically retries on temporary lock errors
- **Usage**: Optional - can be used for critical write operations

## Expected Performance Improvements

### Before Optimizations:
- **Concurrent Users**: ~5-10 users before lock issues
- **Read Operations**: Blocked during writes
- **Write Operations**: Blocked during reads

### After Optimizations:
- **Concurrent Users**: ~30-50 users comfortably
- **Read Operations**: Multiple concurrent readers
- **Write Operations**: One at a time, but faster and less blocking

## WAL Mode Files
When WAL mode is enabled, SQLite creates two additional files:
- `tutor_app.db-wal` - Write-Ahead Log file
- `tutor_app.db-shm` - Shared Memory file

**These files are normal and expected. Do NOT delete them manually.**

## Migration Notes
- WAL mode is enabled automatically on first connection after update
- No data migration required
- Existing database files work seamlessly
- If WAL mode fails (e.g., read-only filesystem), the app continues with default mode

## Testing
To verify WAL mode is active:
```python
from database import get_db_connection
conn = get_db_connection()
print(conn.execute('PRAGMA journal_mode').fetchone()[0])  # Should print 'wal'
conn.close()
```

## Additional Recommendations

### For 50+ Concurrent Users:
1. Consider migrating to PostgreSQL
2. Add connection pooling
3. Implement caching layer (Redis)

### For Current Setup:
- Current optimizations should handle 30-50 concurrent users
- Monitor database lock errors in logs
- Consider adding pagination for large datasets

## Troubleshooting

### Database Lock Errors
If you still see "database is locked" errors:
1. Check if WAL mode is enabled: `PRAGMA journal_mode`
2. Reduce write frequency (batch operations)
3. Use `execute_with_retry()` for critical writes
4. Consider increasing timeout in `get_db_connection()`

### WAL Files Growing Large
- WAL files auto-checkpoint periodically
- Manual checkpoint: `PRAGMA wal_checkpoint(TRUNCATE)`
- Usually not needed, but can be done during maintenance

## References
- [SQLite WAL Mode Documentation](https://www.sqlite.org/wal.html)
- [SQLite Performance Tuning](https://www.sqlite.org/performance.html)


