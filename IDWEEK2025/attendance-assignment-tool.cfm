<cfparam name="url.conference_id" default="1">
<cfparam name="url.confid" default="#url.conference_id#">
<cfsetting showdebugoutput="no">

<!--- Set conference variables --->
<cfset conferenceId = url.confid>
<cfset conferenceName = "IDWeek 2025">
<cfset conferenceDates = "October 19-22, 2025">

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <!-- Put these in <head> -->

    <meta name="api-base"  content="/IDWEEK2025/cfml_viewer/">  <!-- where api_*.cfm endpoints live -->
    <meta name="data-base" content="../"> <!-- where idweek2025_combined.json lives -->
    
    <title><cfoutput>#conferenceName# - Attendance Assignments</cfoutput></title>

    <!-- Custom stylesheet for IDWeek styling -->
    <link rel="stylesheet" href="/assets/css/conference_crawler.css?v=<cfoutput>#application.cachebuster#</cfoutput>">

    <!-- Force calendar to fit in viewport -->
    <style>
    #calendar-container .calendar-grid {
        display: grid !important;
        grid-template-columns: repeat(3, minmax(280px, 1fr)) !important;
        gap: 10px !important;
        width: 100% !important;
        overflow-x: auto !important;
        padding: 10px !important;
        box-sizing: border-box !important;
    }

    #calendar-container .day-column {
        min-width: 280px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .calendar-view {
        width: 100% !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
    }

    .calendar-session {
        padding: 8px !important;
        margin-bottom: 4px !important;
        font-size: 12px !important;
        word-wrap: break-word !important;
        white-space: normal !important;
    }

    .calendar-session .session-title {
        font-size: 12px !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    .calendar-session .session-time {
        font-size: 13px !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
    }
    </style>
</head>
<body>

  <!-- Header -->
  <div class="header">
    <h1><cfoutput>#conferenceName# Assignments - <span style="font-size:24px;">#conferenceDates#</span></cfoutput></h1>
  </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number" id="total-sessions">0</div>
        <div class="stat-label">Sessions</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" id="total-users">0</div>
        <div class="stat-label">MSDs</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" id="total-assignments">0</div>
        <div class="stat-label">Assignments</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" id="conflicts-count">0</div>
        <div class="stat-label">Conflicts</div>
      </div>
    </div>

    <!-- Controls -->
    <div class="controls">
      <div class="control-buttons">
        <input type="file" id="json-upload" accept=".json" style="display: none;">
        <!-- <button class="btn" onclick="document.getElementById('json-upload').click()">📁 Load Sessions JSON</button> -->
        <button class="btn" onclick="showAttendeesBySession()">📋 Attendees by Session</button>
        <button class="btn" onclick="showSessionsByAttendee()">📅 Sessions by Attendee</button>
        <button class="btn" onclick="exportAssignments()">💾 Export Data</button>
        <button class="btn" onclick="generateReports()">📊 Generate Reports</button>
        <!-- <button class="btn" onclick="forceReload()">🔄 Reload Data</button> -->
        <button class="btn btn-danger" onclick="clearAllData()">🗑️ Clear All</button>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left panel: MSDs -->
      <div class="panel">
        <div class="panel-header">
          <span>👥 Medical Science Directors</span>
          <button class="btn btn_header btn-sm" onclick="showAddUserModal()">+ Add</button>
        </div>
        <div class="panel-content">
          <div id="users-container">
            <div class="text-center text-muted">
              No MSDs loaded yet.<br>
              <button class="btn btn-link p-0 mt-2" onclick="showAddUserModal()">Add First MSD</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right panel: Tabs (Sessions / Calendar) -->
      <div class="panel">
          <!-- Tab Navigation -->
          <div class="tab-navigation">
            <button class="tab-button active" onclick="switchTab('sessions')" id="sessions-tab">
              📋 Conference Sessions
            </button>
            <button class="tab-button" onclick="switchTab('calendar')" id="calendar-tab">
              📅 Weekly Calendar View
            </button>
          </div>

          <!-- Sessions Tab Content -->
          <div id="sessions-tab-content" class="tab-content active">
            <div class="panel-header">
              <span id="session-count">0 sessions</span>
              <span><button class="btn_header" id="expand-collapse-all" onclick="toggleAllTimeSlots()">📋 Collapse All</button></span>
            </div>

            <div class="session-filters">
              <input type="text" id="search-input" placeholder="🔍 Search sessions, locations, speakers...">
              <select id="date-filter">
                <option value="">All Dates</option>
              </select>
              <select id="type-filter">
                <option value="">All Types</option>
              </select>
              <button class="btn btn-sm" onclick="clearFilters()">Clear</button>
            </div>

            <div class="panel-content">
              <div id="sessions-container">
                <div class="loading">Loading sessions...</div>
              </div>
            </div>
          </div>

          <!-- Calendar Tab Content -->
          <div id="calendar-tab-content" class="tab-content">
            <div class="panel-header">
              <span id="calendar-summary">Loading calendar...</span>
            </div>
            <div class="calendar-view" id="calendar-container">
              <!-- Calendar will be populated by JavaScript -->
            </div>
          </div>
      </div>
    </div>

  <!-- Add User Modal -->
  <div id="user-modal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h5>Add New Attendee</h5>
        <span class="close" onclick="closeUserModal()">&times;</span>
      </div>
      <div class="modal-body">

        <div class="form-group">
          <label for="user-name">Full Name *</label>
          <input type="text" id="user-name" placeholder="Enter full name">
        </div>

        <div class="form-group">
          <label for="user-email">Email Address *</label>
          <input type="email" id="user-email" placeholder="Enter email address">
        </div>

        <div class="form-group">
          <label for="user-department">Department/Organization</label>
          <input type="text" id="user-department" placeholder="Enter department or organization">
        </div>

        <div class="form-group">
          <label for="user-role">Role</label>
          <select id="user-role">
            <option value="Attendee">Attendee</option>
            <option value="Speaker">Speaker</option>
            <option value="Staff">Staff</option>
            <option value="VIP">VIP</option>
            <option value="Moderator">Moderator</option>
          </select>
        </div>

        <div class="modal-buttons">
          <button class="btn btn-secondary" onclick="closeUserModal()">Cancel</button>
          <button class="btn btn-success" onclick="saveUser()">Save User</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Attendees by Session Modal -->
  <div id="attendees-by-session-modal" class="modal">
    <div class="modal-content modal-lg">
      <div class="modal-header">
        <h5>📋 Attendees by Session</h5>
        <span class="close" onclick="closeAttendeesBySessionModal()">&times;</span>
      </div>
      <div class="modal-body">
        <input type="text" id="session-search" placeholder="🔍 Search sessions...">
        <div id="attendees-by-session-content" style="max-height: 60vh; overflow-y: auto;">
          <!-- Populated by JS -->
        </div>
        <div class="modal-buttons">
          <button class="btn btn-secondary" onclick="closeAttendeesBySessionModal()">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Sessions by Attendee Modal -->
  <div id="sessions-by-attendee-modal" class="modal">
    <div class="modal-content modal-lg">
      <div class="modal-header">
        <h5>📅 Sessions by Attendee</h5>
        <span class="close" onclick="closeSessionsByAttendeeModal()">&times;</span>
      </div>
      <div class="modal-body">
        <input type="text" id="attendee-search" placeholder="🔍 Search attendees...">
        <div id="sessions-by-attendee-content" style="max-height: 60vh; overflow-y: auto;">
          <!-- Populated by JS -->
        </div>
        <div class="modal-buttons">
          <button class="btn btn-secondary" onclick="closeSessionsByAttendeeModal()">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MSD Assignments Modal -->
  <div id="msd-assignments-modal" class="modal">
    <div class="modal-content modal-xl">
      <div class="modal-header">
        <h5 id="msd-assignments-title">👨‍⚕️ MSD Assignments</h5>
        <span class="close" onclick="closeMSDAssignmentsModal()">&times;</span>
      </div>
      <div class="modal-body">
        <div id="msd-assignments-content" style="max-height: 70vh; overflow-y: auto;">
          <!-- Populated by JS -->
        </div>
        <div class="modal-buttons">
          <button class="btn btn-secondary" onclick="closeMSDAssignmentsModal()">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Your app JS -->
  <script src="/assets/js/conference_crawler.js"></script>

  <script>
    // Modal functions using native CSS display
    function showAddUserModal() {
      document.getElementById('user-modal').style.display = 'block';
      document.getElementById('user-name').focus();
    }
    function closeUserModal() {
      document.getElementById('user-modal').style.display = 'none';
    }

    function showAttendeesBySession() {
      document.getElementById('attendees-by-session-modal').style.display = 'block';
    }
    function closeAttendeesBySessionModal() {
      document.getElementById('attendees-by-session-modal').style.display = 'none';
    }

    function showSessionsByAttendee() {
      document.getElementById('sessions-by-attendee-modal').style.display = 'block';
    }
    function closeSessionsByAttendeeModal() {
      document.getElementById('sessions-by-attendee-modal').style.display = 'none';
    }

    function openMSDAssignmentsModal() {
      document.getElementById('msd-assignments-modal').style.display = 'block';
    }
    function closeMSDAssignmentsModal() {
      document.getElementById('msd-assignments-modal').style.display = 'none';
    }

    // Custom tab switching function
    function switchTab(tabName) {
      // Hide all tab contents
      const tabContents = document.querySelectorAll('.tab-content');
      tabContents.forEach(content => {
        content.style.display = 'none';
      });

      // Remove active class from all tab buttons
      const tabButtons = document.querySelectorAll('.tab-button');
      tabButtons.forEach(button => {
        button.classList.remove('active');
      });

      // Show selected tab content
      const selectedTabContent = document.getElementById(tabName + '-tab-content');
      if (selectedTabContent) {
        selectedTabContent.style.display = 'block';
      }

      // Make selected button active
      const selectedButton = document.getElementById(tabName + '-tab');
      if (selectedButton) {
        selectedButton.classList.add('active');
      }

      // If switching to calendar tab, refresh the calendar display
      if (tabName === 'calendar' && typeof renderCalendar === 'function') {
        renderCalendar();
      }
    }

    // Initialize when DOM ready
    document.addEventListener('DOMContentLoaded', function() {
      console.log('DOM loaded, initializing...');
      // Ensure sessions tab is active by default
      switchTab('sessions');

      // Initialize the application
      if (typeof initializeApp === 'function') {
        initializeApp();
      }

      // Fix the collapse button by ensuring proper HTML structure is used
      const originalRenderSessions = window.renderSessions;
      if (originalRenderSessions) {
        window.renderSessions = function() {
          const container = document.getElementById('sessions-container');
          const sessionsToShow = (typeof filteredSessions !== 'undefined' && filteredSessions.length > 0) ? filteredSessions : (typeof sessions !== 'undefined' ? sessions : []);

          if (sessionsToShow.length === 0) {
            container.innerHTML = '<div class="no-data">No sessions match your filters.</div>';
            document.getElementById('session-count').textContent = '0 sessions';
            return;
          }

          container.innerHTML = '';

          // Use the proper structure for collapsible sessions
          if (typeof groupSessions === 'function' && typeof createDateGroupElement === 'function') {
            const dateGroups = groupSessions(sessionsToShow);
            dateGroups.forEach(dateGroup => {
              const dateElement = createDateGroupElement(dateGroup);
              container.appendChild(dateElement);
            });
          } else {
            // Fallback to original function
            originalRenderSessions.call(this);
            return;
          }

          document.getElementById('session-count').textContent = `${sessionsToShow.length} sessions`;
        };
      }
    });
  </script>
</body>
</html>
