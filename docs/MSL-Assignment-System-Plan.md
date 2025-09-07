# MSL Assignment System Plan

## Overview

A web-based system to replace Excel-based MSL assignment workflows for conference sessions and posters. The system needs to maintain Excel-like efficiency while providing centralized, multi-user access for assignment management.

## System Architecture

### 1. Database Design

```sql
-- Core Tables
MSLs (id, name, email, specialty, territory, active)
Sessions (id, title, date, time, track, type, location)  
Posters (id, title, track, session_date, location)
Assignments (id, msl_id, content_id, content_type, priority, notes, assigned_date)
```

### 2. Web UI Strategy - "Excel-like" Efficiency

**Option A: Interactive Grid Interface**
```cfm
<!-- DataTables.js with inline editing -->
<table id="assignmentGrid" class="display">
  <thead>
    <tr><th>Content</th><th>Track</th><th>Date/Time</th><th>Assigned MSL</th><th>Priority</th></tr>
  </thead>
</table>

<script>
// Inline dropdown editing, bulk operations, real-time save
$('#assignmentGrid').DataTable({
    select: 'multi',
    buttons: ['selectAll', 'selectNone', 'bulkAssign']
});
</script>
```

**Option B: Card-Based Drag & Drop**
```cfm
<!-- Kanban-style board -->
<div class="assignment-board">
  <div class="msl-pool">
    <cfloop query="getMSLs">
      <div class="msl-card" data-mslid="#id#">#name#</div>
    </cfloop>
  </div>
  
  <div class="content-columns">
    <cfloop query="getTrackSessions">
      <div class="track-column" data-track="#track#">
        <div class="session-card droppable">#title#</div>
      </div>
    </cfloop>
  </div>
</div>
```

### 3. Recommended Approach: Hybrid Dashboard

**Main Dashboard Features:**
- **Left Panel**: MSL list with availability indicators
- **Center Panel**: Filterable content grid (sessions/posters)
- **Right Panel**: Assignment summary and bulk tools
- **Bottom Panel**: Calendar view for scheduling conflicts

**Core Components:**

```cfm
<!-- assignment_dashboard.cfm -->
<div class="assignment-dashboard">
  
  <!-- MSL Panel -->
  <div class="msl-panel">
    <h3>MSLs <span class="total-count">(#msls.recordCount#)</span></h3>
    <input type="text" id="mslFilter" placeholder="Filter MSLs...">
    <div class="msl-list">
      <cfloop query="getMSLs">
        <div class="msl-item" data-mslid="#id#" data-specialty="#specialty#">
          <strong>#name#</strong>
          <small>#specialty# | #territory#</small>
          <span class="assignment-count">#getCurrentAssignments(id)# assigned</span>
        </div>
      </cfloop>
    </div>
  </div>
  
  <!-- Content Grid Panel -->
  <div class="content-panel">
    <div class="toolbar">
      <select id="contentType">
        <option value="sessions">Sessions</option>
        <option value="posters">Posters</option>
      </select>
      <select id="trackFilter"><option value="">All Tracks</option></select>
      <input type="date" id="dateFilter">
      <button id="bulkAssign">Bulk Assign</button>
    </div>
    
    <table id="contentGrid" class="assignment-table">
      <thead>
        <tr>
          <th><input type="checkbox" id="selectAll"></th>
          <th>Title</th>
          <th>Track</th>
          <th>Date/Time</th>
          <th>Assigned MSL</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="contentTableBody">
        <!-- Dynamic content loaded via AJAX -->
      </tbody>
    </table>
  </div>
  
  <!-- Assignment Tools Panel -->
  <div class="tools-panel">
    <h3>Quick Actions</h3>
    <div class="selected-info">
      <span id="selectedCount">0</span> items selected
    </div>
    
    <div class="bulk-assignment">
      <select id="bulkMSLSelect">
        <option value="">Choose MSL...</option>
        <cfloop query="getMSLs">
          <option value="#id#">#name#</option>
        </cfloop>
      </select>
      <button id="applyBulkAssignment">Assign Selected</button>
    </div>
    
    <div class="assignment-stats">
      <h4>Assignment Summary</h4>
      <div id="assignmentStats">
        <!-- Real-time stats -->
      </div>
    </div>
  </div>
  
</div>
```

## 4. Key JavaScript Functionality

```javascript
// assignment.js - Core functionality
class AssignmentManager {
    constructor() {
        this.selectedItems = new Set();
        this.initializeDataTable();
        this.bindEvents();
    }
    
    initializeDataTable() {
        this.dataTable = $('#contentGrid').DataTable({
            ajax: 'ajax/getContentData.cfm',
            select: 'multi',
            columns: [
                { data: 'checkbox', orderable: false },
                { data: 'title' },
                { data: 'track' },
                { data: 'datetime' },
                { data: 'assigned_msl', render: this.renderMSLDropdown },
                { data: 'actions', orderable: false }
            ]
        });
    }
    
    renderMSLDropdown(data, type, row) {
        return `<select class="msl-assignment" data-contentid="${row.id}">
                    <option value="">Unassigned</option>
                    ${this.getMSLOptions(data)}
                </select>`;
    }
    
    assignMSL(contentId, mslId, contentType) {
        $.post('ajax/assignMSL.cfm', {
            contentId, mslId, contentType
        }).done(() => {
            this.refreshStats();
            this.updateMSLCounts();
        });
    }
    
    bulkAssign() {
        const selectedRows = this.dataTable.rows('.selected').data();
        const mslId = $('#bulkMSLSelect').val();
        
        if (!mslId) return alert('Please select an MSL');
        
        // Batch assignment
        const assignments = selectedRows.map(row => ({
            contentId: row.id,
            contentType: $('#contentType').val()
        }));
        
        this.performBulkAssignment(assignments, mslId);
    }
}
```

## 5. ColdFusion Backend Components

```cfm
<!-- ajax/assignMSL.cfm -->
<cfparam name="form.contentId" type="numeric">
<cfparam name="form.mslId" type="numeric">  
<cfparam name="form.contentType" type="string">

<cftry>
    <cfquery datasource="#application.dsn#">
        INSERT INTO assignments (msl_id, content_id, content_type, assigned_date)
        VALUES (
            <cfqueryparam value="#form.mslId#" cfsqltype="cf_sql_integer">,
            <cfqueryparam value="#form.contentId#" cfsqltype="cf_sql_integer">,
            <cfqueryparam value="#form.contentType#" cfsqltype="cf_sql_varchar">,
            <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
        )
    </cfquery>
    
    <cfset response = {"success": true, "message": "Assignment saved"}>
    
    <cfcatch>
        <cfset response = {"success": false, "error": "#cfcatch.message#"}>
    </cfcatch>
</cftry>

<cfoutput>#serializeJSON(response)#</cfoutput>
```

## 6. Advanced Features

### Smart Assignment Suggestions
- Match MSL specialty to session tracks
- Geographic proximity for in-person events
- Workload balancing
- Conflict detection (scheduling overlaps)

### Export Capabilities
```cfm
<!-- Export back to Excel for final review -->
<cfspreadsheet action="write" 
               query="getAssignments" 
               filename="MSL_Assignments_#dateFormat(now(),'yyyy-mm-dd')#.xlsx">
```

### Real-time Collaboration
- WebSocket updates for multi-user editing
- Assignment locks to prevent conflicts
- Audit trail for changes

## 7. Implementation Priority

### Phase 1: Core Functionality
1. Basic assignment interface
2. MSL and content data integration  
3. Simple assignment CRUD operations

### Phase 2: Enhanced UX
1. Advanced filtering and search
2. Bulk operations
3. Drag & drop interface

### Phase 3: Smart Features
1. Assignment recommendations
2. Conflict detection
3. Analytics and reporting

## Key Advantages Over Excel

1. **Multi-user Access**: Multiple people can work simultaneously
2. **Real-time Updates**: Changes are immediately visible to all users
3. **Data Integrity**: Centralized database prevents version conflicts
4. **Advanced Filtering**: Dynamic filtering and search capabilities
5. **Audit Trail**: Track who made what changes when
6. **Integration**: Can pull directly from conference data sources
7. **Notifications**: Alert MSLs of their assignments automatically

## Technical Requirements

- **Frontend**: HTML5, CSS3, JavaScript (jQuery, DataTables.js)
- **Backend**: ColdFusion, SQL Server/MySQL
- **Libraries**: Bootstrap for responsive design, SortableJS for drag & drop
- **Export**: CFSpreadsheet for Excel generation
- **Real-time**: WebSocket support for collaboration (optional)

## Success Metrics

- Reduce assignment time by 70% compared to Excel workflow
- Enable simultaneous editing by multiple team members
- Provide real-time assignment statistics and conflict detection
- Maintain all Excel-like bulk editing capabilities
- Export final assignments in Excel format for distribution