# Database Migration Guide - ISAVS 2026

## Problem Fixed
Your existing database had tables with missing columns (like `teacher_id` in `classes` table), causing index creation to fail.

## Solution
Created `database_schema_migration_safe.sql` that:
- ✅ Creates tables if they don't exist
- ✅ Adds missing columns to existing tables
- ✅ Adds constraints only if they don't exist
- ✅ Creates indexes only if they don't exist
- ✅ Creates triggers only if they don't exist
- ✅ Handles all edge cases for existing databases

## How to Use

### Option 1: Run the Migration-Safe Schema (Recommended)
```bash
psql -U your_username -d your_database -f database_schema_migration_safe.sql
```

This will:
1. Check your existing tables
2. Add any missing columns
3. Create indexes that don't exist
4. Leave existing data untouched

### Option 2: Fresh Database (Clean Install)
If you want to start fresh:
```bash
# Drop existing database (WARNING: This deletes all data!)
dropdb your_database
createdb your_database

# Run the original schema
psql -U your_username -d your_database -f database_schema.sql
```

## What Was Fixed

### Classes Table
**Before:** Missing `teacher_id`, `created_at`, `updated_at` columns
**After:** All columns added conditionally

### Students Table
**Before:** Missing `user_id`, `approved_by`, `approved_at`, `facial_embedding`, `face_image_base64`
**After:** All columns added conditionally

### All Tables
- All indexes now check for existence before creation
- All constraints now check for existence before creation
- All triggers now check for existence before creation

## Verify Migration Success

After running the migration, check:

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check classes table structure
\d classes

-- Check students table structure
\d students

-- Check all indexes
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

## Expected Output
You should see:
- ✅ 10 tables created
- ✅ All indexes created
- ✅ 3 views created
- ✅ 3 functions created
- ✅ 4 triggers created
- ✅ Sample data inserted
- ✅ Success message: "ISAVS 2026 Database Schema - Migration Complete!"

## Troubleshooting

### If you still get errors:
1. Check PostgreSQL version: `SELECT version();`
2. Check if UUID extension is available: `SELECT * FROM pg_available_extensions WHERE name = 'uuid-ossp';`
3. Check your user permissions: `\du`

### Common Issues:
- **Permission denied**: Your user needs CREATE privileges
- **Extension not found**: Install postgresql-contrib package
- **Foreign key violations**: Make sure referenced tables exist first

## Next Steps
After successful migration:
1. ✅ Verify all tables and columns exist
2. ✅ Test inserting sample data
3. ✅ Run the backend server
4. ✅ Test the dual portal system (Teacher Port 2001, Student Port 2002)

## Files
- `database_schema_migration_safe.sql` - Use this for existing databases
- `database_schema.sql` - Original schema (for fresh installs)
