# Database Setup for Conference Assignment Tool

## Overview
The CFM version of the attendance assignment tool now includes database connectivity to save assignments permanently instead of using localStorage only.

## Files Created
1. `api_users.cfm` - Retrieves users/MSDs from database
2. `api_sessions.cfm` - Retrieves conference sessions from database
3. `api_save.cfm` - Saves user-session assignments to database
4. `database_setup.sql` - SQL script to create required tables

## Database Configuration

### 1. Update Datasource Name
In each API file (`api_users.cfm`, `api_sessions.cfm`, `api_save.cfm`), update this line:
```cfml
<cfset dsn = "your_datasource_name">
```
Replace `"your_datasource_name"` with your actual ColdFusion datasource name.

### 2. Create Database Tables
Run the SQL script `database_setup.sql` in your SQL Server database to create:
- `conference_users` - Stores MSDs and attendees
- `conference_sessions` - Stores conference session data
- `conference_assignments` - Stores user-session assignments

### 3. Data Population

#### Option A: Use Existing Data
If you have session data in JSON format, you can import it into the `conference_sessions` table.

#### Option B: Use Default MSDs
The setup script creates two default MSDs:
- Nancy Rabasco (nancy.rabasco@example.com)
- Besu Teshome (besu.teshome@example.com)

## How It Works

### Database Flow
1. **Load MSDs**: `api_users.cfm` queries `conference_users` table
2. **Load Sessions**: `api_sessions.cfm` queries `conference_sessions` table
3. **Save Assignments**: `api_save.cfm` saves to `conference_assignments` table

### Fallback System
- If database APIs fail, the system automatically falls back to localStorage
- Users will see appropriate messages indicating which storage method is being used

### Assignment Process
1. User selects an MSD from the left panel
2. User clicks "Assign" button on a session
3. JavaScript calls `api_save.cfm` via POST request
4. Assignment is saved to `conference_assignments` table
5. UI updates to show the assignment

## Testing Database Connectivity

### Check API Endpoints
1. Visit: `http://yourserver/IDWEEK2025/cfml_viewer/api_users.cfm?conference_id=1`
2. Should return JSON with user data
3. Visit: `http://yourserver/IDWEEK2025/cfml_viewer/api_sessions.cfm?conference_id=1`
4. Should return JSON with session data

### Expected Behavior
- **Database Working**: Console shows "Successfully saved assignments to database"
- **Database Not Working**: Console shows "Database API not available, using localStorage fallback"

## Troubleshooting

### Common Issues
1. **Datasource Error**: Update the `dsn` variable in API files
2. **Table Not Found**: Run the `database_setup.sql` script
3. **Permission Error**: Ensure ColdFusion has database access
4. **CORS Issues**: Add appropriate headers if needed

### Console Messages
- `💾 Attempting to save to database...` - Database save starting
- `✅ Successfully saved assignments to database` - Database save successful
- `❌ Database API error` - Database connection failed
- `⚠️ Database API not available, using localStorage fallback` - Fallback activated

## Migration from localStorage
If you have existing assignments in localStorage, they will continue to work alongside the database system. New assignments will be saved to the database when available.