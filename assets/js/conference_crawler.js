// ---- BASE PATHS ----
const API_BASE  = document.querySelector('meta[name="api-base"]')?.content || './';
const DATA_BASE = document.querySelector('meta[name="data-base"]')?.content || './';

function apiUrl(path)  { return API_BASE.replace(/\/?$/, '/')  + path.replace(/^\//, ''); }
function dataUrl(path) { return DATA_BASE.replace(/\/?$/, '/') + path.replace(/^\//, ''); }

// Global application state
let sessions = [];
let users = [];
let assignments = {}; // sessionId -> [userIds]
let selectedUser = null;
let filteredSessions = [];

// Conference ID will be determined from URL parameters

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing IDWeek 2025 Attendance Tool...');
    console.log('🔍 Testing modal functions availability...');
    console.log('showAttendeesBySession function:', typeof window.showAttendeesBySession);
    console.log('showSessionsByAttendee function:', typeof window.showSessionsByAttendee);
    setupEventHandlers();
    // Load MSD data first, then check for stored data
    loadMSDData();
    loadSessionsData();
});

function setupEventHandlers() {
    // File upload
    document.getElementById('json-upload').addEventListener('change', handleFileUpload);

    // Search and filters
    document.getElementById('search-input').addEventListener('input', filterSessions);
    document.getElementById('date-filter').addEventListener('change', filterSessions);
    document.getElementById('type-filter').addEventListener('change', filterSessions);

    // Modal controls
    window.addEventListener('click', function(event) {
        if (event.target.id === 'user-modal') {
            closeUserModal();
        } else if (event.target.id === 'attendees-by-session-modal') {
            closeAttendeesBySessionModal();
        } else if (event.target.id === 'sessions-by-attendee-modal') {
            closeSessionsByAttendeeModal();
        } else if (event.target.id === 'duplicate-assignment-modal') {
            closeDuplicateAssignmentModal();
        } else if (event.target.id === 'msd-assignments-modal') {
            closeMSDAssignmentsModal();
        }
    });
}

function getConferenceId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('confid') || urlParams.get('conference_id') || '1'; // Default to 1 if not specified
}

function loadMSDData() {
  console.log('Loading Medical Science Directors from database...');
  const conferenceId = getConferenceId();
  console.log('🔍 Using conference ID:', conferenceId);

  // Build the actual URL string
  const timestamp = Date.now();
  const usersUrl = apiUrl(`api_conference_users.cfm?confid=${conferenceId}&_t=${timestamp}`);
  console.log('🔍 Attempting to fetch from:', usersUrl);

  fetch(usersUrl)
    .then(response => {
      console.log('🌐 API Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }
      return response.json();
    })
    .then(data => {
            console.log('✅ Successfully loaded', data.length, 'conference users from DATABASE');
            console.log('🔍 Raw database users:', data);

            // Process users data
            users = data.map((dbUser, index) => {
                console.log('🔍 Processing user:', dbUser);

                // Handle different field naming conventions
                const userId = dbUser.user_id || dbUser.id || dbUser.USER_ID || dbUser.ID || (index + 1);
                const firstName = dbUser.firstname || dbUser.FIRSTNAME || dbUser.FIRST_NAME || dbUser.FirstName || '';
                const lastName = dbUser.lastname || dbUser.LASTNAME || dbUser.LAST_NAME || dbUser.LastName || '';
                const email = dbUser.email || dbUser.EMAIL || '';
                const department = dbUser.department || dbUser.DEPARTMENT || '';
                const role = dbUser.role || dbUser.ROLE || 'MSD';
                const assignedDate = dbUser.ASSIGNED_DATE || dbUser.assigned_date || dbUser.AssignedDate;
                const createdAt = dbUser.CREATED_AT || dbUser.created_at || dbUser.CreatedAt;

                // Construct full name
                let fullName = '';
                console.log('🔍 Name construction for user:', {
                    firstName, lastName,
                    FULL_NAME: dbUser.FULL_NAME,
                    full_name: dbUser.full_name,
                    name: dbUser.name,
                    email
                });

                if (firstName && lastName) {
                    fullName = `${firstName} ${lastName}`.trim();
                    console.log('✅ Using firstName + lastName:', fullName);
                } else if (dbUser.name || dbUser.NAME || dbUser.FULL_NAME || dbUser.full_name) {
                    fullName = dbUser.name || dbUser.NAME || dbUser.FULL_NAME || dbUser.full_name;
                    console.log('✅ Using full name field:', fullName);
                } else {
                    fullName = email.split('@')[0]; // fallback to email username
                    console.log('⚠️ Falling back to email username:', fullName);
                }

                const processedUser = {
                    id: userId,
                    userId: userId,
                    name: fullName,
                    firstname: firstName,
                    lastname: lastName,
                    email: email,
                    department: department,
                    role: role,
                    assignedDate: assignedDate,
                    createdAt: createdAt || new Date().toISOString()
                };

                console.log('🔍 Mapped user:', processedUser);
                return processedUser;
            });

            console.log('✅ Final users array:', users);
            renderUsersMin();
            updateStats();
            showSuccessMessage(`Loaded ${users.length} conference users!`);

            // Load stored assignments after MSDs are loaded
            loadStoredData();
        })
        .catch(error => {
            console.log('⚠️ Database API not available, using JSON fallback:', error.message);

            // Use default MSDs when database fails
            console.log('Creating default MSDs since database is not available...');
            users = [
                {
                    id: 1,
                    userId: 1,
                    name: 'Nancy Rabasco',
                    firstname: 'Nancy',
                    lastname: 'Rabasco',
                    email: 'nancy.rabasco@example.com',
                    department: 'Medical Affairs',
                    role: 'MSD',
                    assignedDate: new Date().toISOString(),
                    createdAt: new Date().toISOString()
                },
                {
                    id: 2,
                    userId: 2,
                    name: 'Besu Teshome',
                    firstname: 'Besu',
                    lastname: 'Teshome',
                    email: 'besu.teshome@example.com',
                    department: 'Medical Affairs',
                    role: 'MSD',
                    assignedDate: new Date().toISOString(),
                    createdAt: new Date().toISOString()
                }
            ];
            renderUsersMin();
            updateStats();
            showSuccessMessage(`Created ${users.length} default MSDs (database not available)`);

            // Load stored assignments after MSDs are loaded
            loadStoredData();
        });
}

function loadSessionsData() {
    console.log('Loading combined sessions and posters data...');

    // Load combined data file
    fetch(dataUrl('idweek2025_combined.json'))
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(allSessions => {
            console.log(`Successfully loaded ${allSessions.length} items`);

            // Count by type for debugging
            const typeCounts = {};
            allSessions.forEach(item => {
                const type = item.session_info?.type || 'Unknown';
                typeCounts[type] = (typeCounts[type] || 0) + 1;
            });

            console.log('Data breakdown:', typeCounts);
            console.log('Sample item:', allSessions[0]);

            if (allSessions.length === 0) {
                document.getElementById('sessions-container').innerHTML = `
                    <div class="no-data">
                        <h3>No Data Found</h3>
                        <p>Could not load sessions or posters</p>
                        <button class="btn" onclick="document.getElementById('json-upload').click()">
                            📁 Upload Sessions File
                        </button>
                    </div>
                `;
                return;
            }

            sessions = allSessions;
            console.log('✅ Assigned', allSessions.length, 'sessions to global sessions variable');
            processSessionsData();
            // Don't render sessions immediately - wait for assignments to load
            updateStats();

            const posterCount = typeCounts['Poster'] || 0;
            const sessionCount = allSessions.length - posterCount;

            let message = `Loaded ${allSessions.length} items total`;
            if (sessionCount > 0 && posterCount > 0) {
                message = `Loaded ${sessionCount} sessions + ${posterCount} posters (${allSessions.length} total)`;
            } else if (sessionCount > 0) {
                message = `Loaded ${sessionCount} sessions`;
            } else if (posterCount > 0) {
                message = `Loaded ${posterCount} posters`;
            }

            showSuccessMessage(message);

            // Trigger initial render if no assignments will load
            setTimeout(() => {
                console.log('🔍 Checking assignments for initial render...');
                console.log('🔍 assignments keys:', Object.keys(assignments));
                console.log('🔍 assignments length:', Object.keys(assignments).length);
                if (Object.keys(assignments).length === 0) {
                    console.log('✅ No assignments detected, rendering sessions now...');
                    renderSessions();
                } else {
                    console.log('⏳ Assignments exist, not rendering sessions yet');
                }
            }, 500);
        })
        .catch(error => {
            console.error('Failed to load combined data:', error);
            console.error('Make sure idweek2025_combined.json exists and is valid JSON');
            document.getElementById('sessions-container').innerHTML = `
                <div class="no-data">
                    <h3>Error Loading Data</h3>
                    <p>Could not load idweek2025_combined.json</p>
                    <button class="btn" onclick="document.getElementById('json-upload').click()">
                        📁 Upload Sessions File
                    </button>
                </div>
            `;
        });
}

function processSessionsData() {
    console.log(`Processing ${sessions.length} sessions...`);

    // Deduplicate sessions based on title, date, time, and location
    const sessionMap = new Map();
    const duplicateGroups = new Map();

    sessions.forEach(session => {
        const key = createSessionKey(session);

        if (sessionMap.has(key)) {
            // This is a duplicate - group with the first occurrence
            if (!duplicateGroups.has(key)) {
                duplicateGroups.set(key, [sessionMap.get(key)]);
            }
            duplicateGroups.get(key).push(session);
        } else {
            // This is the first occurrence
            sessionMap.set(key, session);
        }
    });

    // Replace sessions array with deduplicated sessions
    const originalCount = sessions.length;
    sessions = Array.from(sessionMap.values());

    // Merge assignments from duplicate sessions
    mergeAssignmentsFromDuplicates(duplicateGroups);

    console.log(`Deduplicated from ${originalCount} to ${sessions.length} sessions`);
    if (duplicateGroups.size > 0) {
        console.log(`Found ${duplicateGroups.size} session groups with duplicates`);
    }

    // Extract unique dates and session types for filters
    const dates = new Set();
    const types = new Set();

    sessions.forEach(session => {
        const date = session.schedule?.date;
        const type = session.session_info?.type;

        if (date) dates.add(date);
        if (type) types.add(type);
    });

    console.log('Unique types found:', Array.from(types));
    console.log('Total sessions processed:', sessions.length);

    // Populate date filter
    const dateFilter = document.getElementById('date-filter');
    if (dateFilter) {
        dateFilter.innerHTML = '<option value="">All Dates</option>';
        // Sort dates chronologically, not alphabetically
        Array.from(dates).sort((a, b) => {
            const dateA = new Date(a);
            const dateB = new Date(b);
            return dateA - dateB;
        }).forEach(date => {
            dateFilter.innerHTML += `<option value="${date}">${formatDate(date)}</option>`;
        });
    }

    // Populate type filter
    const typeFilter = document.getElementById('type-filter');
    if (typeFilter) {
        typeFilter.innerHTML = '<option value="">All Types</option>';
        Array.from(types).sort().forEach(type => {
            typeFilter.innerHTML += `<option value="${type}">${type}</option>`;
        });
    }
}

function createSessionKey(session) {
    // Create a unique key for deduplication based on core session properties
    const title = session.session_info?.title || '';
    const date = session.schedule?.date || '';
    const time = session.schedule?.time || '';
    const location = session.schedule?.location || '';
    const type = session.session_info?.type || '';

    return `${title}|||${date}|||${time}|||${location}|||${type}`;
}

function mergeAssignmentsFromDuplicates(duplicateGroups) {
    // When we have duplicate sessions, we need to merge assignments
    // The first session in each group becomes the "canonical" session
    duplicateGroups.forEach((sessionGroup, key) => {
        if (sessionGroup.length > 1) {
            const canonicalSession = sessionGroup[0];
            const canonicalId = getSessionId(canonicalSession);

            // Merge assignments from all duplicate sessions into the canonical one
            for (let i = 1; i < sessionGroup.length; i++) {
                const duplicateId = getSessionId(sessionGroup[i]);

                if (assignments[duplicateId]) {
                    if (!assignments[canonicalId]) {
                        assignments[canonicalId] = [];
                    }

                    // Add any users from the duplicate that aren't already assigned to canonical
                    assignments[duplicateId].forEach(userId => {
                        if (!assignments[canonicalId].includes(userId)) {
                            assignments[canonicalId].push(userId);
                        }
                    });

                    // Remove the duplicate assignment entry
                    delete assignments[duplicateId];
                }
            }
        }
    });
}

function getSessionId(session) {
    // Try different possible ID fields, including poster sessions
    return session.session_id || session.id || session.Session_ID || session.ID ||
            session.sessionId || session.presentation_number || session.abstractNumber ||
            session.presentation_details?.id || // For poster sessions like P-752
            `session_${Math.random().toString(36).substr(2, 9)}`;
}

function getSessionTitle(session) {
    return session.session_info?.title ||
            session.title ||
            session.session_title ||
            session.name ||
            session.presentation_details?.title || // For poster sessions like P-752
            `Session ${getSessionId(session)}`;
}

function formatDate(dateStr) {
    // Convert "Sunday, October 19, 2025" to "Sun Oct 19"
    if (!dateStr) return 'TBD';
    const parts = dateStr.split(', ');
    if (parts.length >= 2) {
        const day = parts[0].substring(0, 3);
        const monthDay = parts[1].split(' ');
        if (monthDay.length >= 2) {
            return `${day} ${monthDay[0].substring(0, 3)} ${monthDay[1]}`;
        }
    }
    return dateStr;
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            sessions = data;
            console.log(`Loaded ${sessions.length} sessions from file`);
            processSessionsData();
            renderSessions();
            updateStats();
            showSuccessMessage(`Successfully loaded ${sessions.length} sessions!`);
        } catch (error) {
            showErrorMessage('Error parsing JSON file: ' + error.message);
        }
    };
    reader.readAsText(file);
}

function filterSessions() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    const dateFilter = document.getElementById('date-filter').value;
    const typeFilter = document.getElementById('type-filter').value;

    // First, filter by search and date to get available sessions
    let availableSessions = sessions.filter(session => {
        // Search filter
        if (searchTerm) {
            const title = session.session_info?.title?.toLowerCase() || '';
            const location = session.schedule?.location?.toLowerCase() || '';
            const speakerNames = getSpeakerNames(session).toLowerCase();

            if (!title.includes(searchTerm) &&
                !location.includes(searchTerm) &&
                !speakerNames.includes(searchTerm)) {
                return false;
            }
        }

        // Date filter
        if (dateFilter && session.schedule?.date !== dateFilter) {
            return false;
        }

        return true;
    });

    // Update type filter options based on available sessions
    updateTypeFilterOptions(availableSessions);

    // Apply type filter to get final results
    filteredSessions = availableSessions.filter(session => {
        // Type filter
        if (typeFilter && session.session_info?.type !== typeFilter) {
            return false;
        }

        return true;
    });

    renderSessions();
}

function updateTypeFilterOptions(availableSessions) {
    const typeFilter = document.getElementById('type-filter');
    const currentValue = typeFilter.value;

    // Get unique types from available sessions
    const availableTypes = new Set();
    availableSessions.forEach(session => {
        const type = session.session_info?.type;
        if (type) availableTypes.add(type);
    });

    // Rebuild type filter options
    typeFilter.innerHTML = '<option value="">All Types</option>';
    Array.from(availableTypes).sort().forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        if (currentValue === type) {
            option.selected = true;
        }
        typeFilter.appendChild(option);
    });
}

function getSpeakerNames(session) {
    const speakers = session.speakers || {};
    let names = [];

    if (typeof speakers === 'object') {
        Object.values(speakers).forEach(speakerList => {
            if (Array.isArray(speakerList)) {
                speakerList.forEach(speaker => {
                    if (speaker.name) names.push(speaker.name);
                });
            }
        });
    }

    return names.join(' ');
}

function renderSessions() {
    const container = document.getElementById('sessions-container');
    const sessionsToShow = filteredSessions.length > 0 ? filteredSessions : sessions;

    if (sessionsToShow.length === 0) {
        container.innerHTML = '<div class="no-data">No sessions match your filters.</div>';
        document.getElementById('session-count').textContent = '0 sessions';
        return;
    }

    container.innerHTML = '';

    // Group sessions by date, then time slots
    const dateGroups = groupSessions(sessionsToShow);

    if (dateGroups.length === 0) {
        container.innerHTML = '<div class="no-data">No session groups could be created.</div>';
        return;
    }

    // Create a simple list format instead of complex structure
    let html = '';
    dateGroups.forEach(dateGroup => {
        html += `<div style="margin-bottom: 20px; border: 1px solid #ccc; padding: 10px;">`;
        html += `<h3 style="color: #333; margin-bottom: 10px;">${dateGroup.date}</h3>`;

        dateGroup.timeSlots.forEach(timeSlot => {
            html += `<div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa;">`;
            html += `<h4 style="color: #666; margin-bottom: 8px;">🕐 ${timeSlot.time}</h4>`;

            timeSlot.sessions.forEach(session => {
                const title = session.session_info?.title || 'Untitled Session';
                const location = session.schedule?.location || 'TBD';
                const type = session.session_info?.type || 'General';

                html += `<div style="padding: 8px; margin-bottom: 5px; background: white; border-left: 4px solid #007bff;">`;
                html += `<strong>${title}</strong><br>`;
                html += `📍 ${location} | 📋 ${type}`;
                html += `</div>`;
            });

            html += `</div>`;
        });

        html += `</div>`;
    });

    container.innerHTML = html;
    document.getElementById('session-count').textContent = `${sessionsToShow.length} sessions`;

    // Debug: Check if tab is active
    setTimeout(() => {
        const tabPane = document.getElementById('sessions-tab-content');
        const tabLink = document.getElementById('sessions-tab');
        console.log('🔍 Tab pane classes:', tabPane?.className);
        console.log('🔍 Tab link classes:', tabLink?.className);
        console.log('🔍 Tab pane display:', window.getComputedStyle(tabPane).display);

        // Force the tab to be active
        if (tabPane) {
            tabPane.classList.add('active', 'show');
            tabPane.classList.remove('fade');
            console.log('🔧 Forced tab pane to be active and show');
        }
        if (tabLink) {
            tabLink.classList.add('active');
            tabLink.setAttribute('aria-selected', 'true');
            console.log('🔧 Forced tab link to be active');
        }
    }, 100);
}

function compareTimeStrings(timeA, timeB) {
    // Helper function to convert time string to comparable number
    function timeToMinutes(timeStr) {
        if (!timeStr || timeStr === 'TBD') return 9999; // Put TBD at end

        // Extract the start time from ranges like "8:00 AM - 12:00 PM"
        const startTime = timeStr.split('-')[0].trim();

        // Handle various time formats
        const timeRegex = /(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?/;
        const match = startTime.match(timeRegex);

        if (!match) {
            // If no time format found, use string comparison
            return timeStr.localeCompare ? 0 : 9999;
        }

        let hours = parseInt(match[1]);
        const minutes = parseInt(match[2]);
        const ampm = match[3] ? match[3].toLowerCase() : '';

        // Convert to 24-hour format
        if (ampm === 'pm' && hours !== 12) {
            hours += 12;
        } else if (ampm === 'am' && hours === 12) {
            hours = 0;
        }

        return hours * 60 + minutes;
    }

    const minutesA = timeToMinutes(timeA);
    const minutesB = timeToMinutes(timeB);

    return minutesA - minutesB;
}

function groupSessions(sessionsToShow) {
    console.log('🔍 Grouping sessions:', sessionsToShow.length);
    console.log('🔍 Sample session data:', sessionsToShow.length > 0 ? sessionsToShow[0] : 'No sessions');

    // Group sessions by date first
    const dateGroups = new Map();

    sessionsToShow.forEach(session => {
        const date = session.schedule?.date || 'TBD';

        if (!dateGroups.has(date)) {
            dateGroups.set(date, new Map());
        }

        const timeSlots = dateGroups.get(date);
        const time = session.schedule?.time || 'TBD';

        if (!timeSlots.has(time)) {
            timeSlots.set(time, []);
        }

        timeSlots.get(time).push(session);
    });

    // Convert to ordered array format
    const sortedDates = Array.from(dateGroups.keys()).sort((a, b) => {
        if (a === 'TBD') return 1;
        if (b === 'TBD') return -1;
        return new Date(a) - new Date(b);
    });

    console.log('Date groups (chronological):', sortedDates);

    const result = sortedDates.map(date => {
        const timeSlots = dateGroups.get(date);
        const sortedTimeSlots = Array.from(timeSlots.entries())
            .sort(([timeA], [timeB]) => {
                if (timeA === 'TBD') return 1;
                if (timeB === 'TBD') return -1;
                // Enhanced time comparison for various formats
                return compareTimeStrings(timeA, timeB);
            })
            .map(([time, sessions]) => ({
                time,
                sessions
            }));

        const totalSessions = sortedTimeSlots.reduce((sum, slot) => sum + slot.sessions.length, 0);

        console.log(`Date ${date}: ${sortedTimeSlots.length} time slots, ${totalSessions} total sessions`);

        return {
            date,
            timeSlots: sortedTimeSlots,
            totalSessions
        };
    });

    console.log('🔍 Final date groups created:', result.length);
    console.log('🔍 Sample date group:', result.length > 0 ? result[0] : 'No groups');
    return result;
}

function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('date-filter').value = '';
    document.getElementById('type-filter').value = '';
    filteredSessions = [];
    renderSessions();
}

// Populate date filter
function populateDateFilter() {
    const dateFilter = document.getElementById('date-filter');
    const dates = new Set();

    sessions.forEach(session => {
        const date = session.schedule?.date;
        if (date) dates.add(date);
    });

    // Sort dates chronologically
    const sortedDates = Array.from(dates).sort((a, b) => new Date(a) - new Date(b));

    sortedDates.forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        option.textContent = formatDate(date);
        dateFilter.appendChild(option);
    });
}

function toggleDateGroup(dateHeader) {
    const dateContent = dateHeader.nextElementSibling;
    const caret = dateHeader.querySelector('.date-caret');

    if (dateContent.style.display === 'none') {
        // Expand
        dateContent.style.display = 'block';
        caret.textContent = '▼';
    } else {
        // Collapse
        dateContent.style.display = 'none';
        caret.textContent = '▶';
    }
}

function toggleAllTimeSlots() {
    const dateHeaders = document.querySelectorAll('.date-header');
    const button = document.getElementById('expand-collapse-all');

    let hasExpanded = false;

    // Check if any are currently expanded
    dateHeaders.forEach(header => {
        const content = header.nextElementSibling;
        if (content && content.style.display !== 'none') {
            hasExpanded = true;
        }
    });

    // Toggle all to opposite state
    dateHeaders.forEach(header => {
        const content = header.nextElementSibling;
        const caret = header.querySelector('.date-caret');

        if (hasExpanded) {
            // Collapse all
            content.style.display = 'none';
            caret.textContent = '▶';
        } else {
            // Expand all
            content.style.display = 'block';
            caret.textContent = '▼';
        }
    });

    // Update button text
    button.textContent = hasExpanded ? '📋 Expand All' : '📋 Collapse All';
}

function createDateGroupElement(dateGroup) {
    const div = document.createElement('div');
    div.className = 'date-group';

    const totalAssignments = dateGroup.timeSlots.reduce((sum, timeSlot) => {
        return sum + timeSlot.sessions.reduce((sessionSum, session) => {
            return sessionSum + (assignments[getSessionId(session)] || []).length;
        }, 0);
    }, 0);

    div.innerHTML = `
        <div class="date-header" onclick="toggleDateGroup(this)">
            <div class="date-caret">▼</div>
            <div class="date-title">📅 ${formatDate(dateGroup.date)}</div>
            <div class="date-stats">
                ${dateGroup.timeSlots.length} time slot(s) • ${dateGroup.totalSessions} session(s) • ${totalAssignments} assignment(s)
            </div>
        </div>
        <div class="date-content">
            ${dateGroup.timeSlots.map(timeSlot => createTimeSlotElement(timeSlot)).join('')}
        </div>
    `;

    return div;
}

function createTimeSlotElement(timeSlot) {
    const totalAssignments = timeSlot.sessions.reduce((sum, session) => {
        return sum + (assignments[getSessionId(session)] || []).length;
    }, 0);

    return `
        <div class="time-slot-group">
            <div class="time-slot-header" onclick="toggleTimeSlot(this)">
                <div class="time-slot-info">
                    <div class="time-slot-caret">▼</div>
                    <div class="time-slot-time">🕐 ${timeSlot.time}</div>
                </div>
                <div class="time-slot-stats">
                    ${timeSlot.sessions.length} session(s) • ${totalAssignments} assignment(s)
                </div>
            </div>
            <div class="time-slot-content">
                ${timeSlot.sessions.map(session => createGroupedSessionHTML(session, null)).join('')}
            </div>
        </div>
    `;
}

function createGroupedSessionHTML(session, groupLocation) {
    const sessionAssignments = assignments[getSessionId(session)] || [];
    const assignedUsers = sessionAssignments.map(userId =>
        users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId))
    ).filter(Boolean);

    const conflicts = selectedUser ? getConflicts(selectedUser.id, session) : [];
    const hasConflict = selectedUser && !sessionAssignments.some(id => id == selectedUser.id) && hasTimeConflict(selectedUser.id, session);

    // Debug logging for assign button visibility
    if (!selectedUser) {
        //console.log('🔍 DEBUG: No selectedUser set, buttons will not show');
    } else {
        // Debug logging disabled to prevent console spam
    }

    // Use individual session location if different from group location
    const sessionLocation = session.schedule?.location || groupLocation || 'TBD';
    const showLocation = sessionLocation !== groupLocation;

    const hasAssignments = sessionAssignments.length > 0;
    const isCollapsed = false; // FIXED: Don't auto-collapse sessions

    //console.log(`Creating grouped session ${getSessionId(session)}: hasAssignments=${hasAssignments}, isCollapsed=${isCollapsed}, assignments:`, sessionAssignments);

    return `
        <div class="simple-session ${hasAssignments ? 'assigned' : 'unassigned'}" data-session-id="${getSessionId(session)}">
            <div class="simple-session-header">
                <div class="simple-session-title">${getSessionTitle(session)}</div>
                <div class="simple-session-controls">
                    ${selectedUser ? `
                        ${hasConflict ? `
                            <button class="btn btn-sm" style="background: #ffc107; color: #333; border: 1px solid #f0ad4e;"
                                    onclick="toggleAssignment('${getSessionId(session)}', ${selectedUser.id})"
                                    title="⚠️ Time conflict - cannot attend multiple sessions simultaneously">
                                ⚠️ Conflict
                            </button>
                        ` : `
                            <button class="btn btn-sm ${sessionAssignments.some(id => id == selectedUser.id) ? 'btn-danger' : 'btn-success'}"
                                    onclick="toggleAssignment('${getSessionId(session)}', ${selectedUser.id})">
                                ${sessionAssignments.some(id => id == selectedUser.id) ? 'Remove' : 'Assign'}
                            </button>
                        `}
                    ` : '<span style="color: #999; font-size: 12px;">Select user to assign</span>'}
                </div>
            </div>
            <div class="simple-session-meta">
                <div class="simple-session-info">
                    ${showLocation ? `<span class="meta-inline-item">📍 ${sessionLocation}</span>` : ''}
                    <span class="meta-inline-item">📋 ${session.session_info?.type || 'General'}</span>
                    <span class="meta-inline-item">🎯 ${session.tracks?.primary_track || 'General'}</span>
                </div>
                <div class="simple-session-assignee ${hasAssignments ? 'has-assignees' : ''}">
                    ${hasAssignments ? assignedUsers.map(u => u.name).join(', ') : ''}
                </div>
            </div>
        </div>
    `;
}

// Conflict tooltip functions
function showConflictTooltip(event, userName, conflictsString) {
    // Simple implementation - just show browser tooltip for now
    console.log(`⚠️ Conflict for ${userName}: ${conflictsString}`);
}

function hideConflictTooltip() {
    // Simple implementation - no action needed for browser tooltip
}

function createSessionElement(session) {
    const div = document.createElement('div');
    const sessionId = getSessionId(session);
    const sessionAssignments = assignments[sessionId] || [];
    const hasAssignments = sessionAssignments.length > 0;
    const isCollapsed = false; // FIXED: Don't auto-collapse sessions


    div.className = `session-item ${hasAssignments ? 'assigned' : 'unassigned'} ${isCollapsed ? 'collapsed' : 'expanded'}`;
    div.dataset.sessionId = sessionId;

    const assignedUsers = sessionAssignments.map(userId =>
        users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId))
    ).filter(Boolean);

    const conflicts = selectedUser ? getConflicts(selectedUser.id, session) : [];
    const hasConflict = selectedUser && !sessionAssignments.some(id => id == selectedUser.id) && hasTimeConflict(selectedUser.id, session);

    div.innerHTML = `
        <div class="session-header" onclick="toggleSessionCollapse('${getSessionId(session)}')" style="cursor: pointer;">
            <div class="session-main-info">
                <div class="session-title">${getSessionTitle(session)}</div>
                <div class="session-meta-inline">
                    <span class="meta-inline-item">📍 ${session.schedule?.location || 'TBD'}</span>
                    <span class="meta-inline-item">📋 ${session.session_info?.type || 'General'}</span>
                    <span class="meta-inline-item">🎯 ${session.tracks?.primary_track || 'General'}</span>
                </div>
                ${hasAssignments ? `<div class="assignment-summary">✅ ${assignedUsers.length} MSD${assignedUsers.length !== 1 ? 's' : ''} assigned: ${assignedUsers.map(u => u.name).join(', ')}</div>` : ''}
            </div>
            <div class="session-controls">
                ${selectedUser ? `
                    <button class="btn btn-sm ${sessionAssignments.some(id => id == selectedUser.id) ? 'btn-danger' : hasConflict ? 'btn' : 'btn-success'}"
                            onclick="event.stopPropagation(); toggleAssignment('${getSessionId(session)}', ${selectedUser.id})"
                            ${hasConflict ? 'style="background: #ffc107; color: #333; border: 1px solid #f0ad4e;" title="⚠️ Time conflict - cannot attend multiple sessions simultaneously"' : ''}>
                        ${sessionAssignments.some(id => id == selectedUser.id) ? '➖ Remove' : hasConflict ? '⚠️ Conflict' : '➕ Assign'}
                    </button>
                ` : '<span style="color: #999; font-size: 12px;">Select user to assign</span>'}
                <span class="collapse-indicator">${isCollapsed ? '📁' : '📂'}</span>
            </div>
        </div>

        <div class="session-details" style="display: ${isCollapsed ? 'none' : 'block'}">
            <div class="session-meta">
                <div class="meta-item">
                    <strong>📅 Date</strong>
                    ${formatDate(session.schedule?.date) || 'TBD'}
                </div>
                <div class="meta-item">
                    <strong>🕐 Time</strong>
                    ${session.schedule?.time || 'TBD'}
                </div>
                <div class="meta-item">
                    <strong>📍 Location</strong>
                    ${session.schedule?.location || 'TBD'}
                </div>
                <div class="meta-item">
                    <strong>📋 Type</strong>
                    ${session.session_info?.type || 'General'}
                </div>
            </div>

            ${Object.keys(session.speakers || {}).length > 0 ? `
                <div class="speakers-section">
                    <h4>👥 Speakers</h4>
                    ${Object.entries(session.speakers).map(([role, speakerList]) => `
                        <div class="speaker-group">
                            <strong>${role}:</strong>
                            ${Array.isArray(speakerList) ? speakerList.map(speaker => `
                                <div class="speaker">
                                    ${speaker.name}
                                    ${speaker.affiliation ? `<span class="affiliation">${speaker.affiliation}</span>` : ''}
                                </div>
                            `).join('') : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            <div class="assignment-section">
                <h4>🎯 Assignment Status</h4>
                <div class="assignment-list">
                    ${assignedUsers.length > 0 ? assignedUsers.map(user => `
                        <div class="assigned-user">
                            <span class="user-info">
                                ${user.name}
                                <br><small>${user.email}</small>
                            </span>
                            <button class="btn btn-sm btn-danger" onclick="removeAssignment('${getSessionId(session)}', ${user.id})" title="Remove assignment">
                                ➖ Remove
                            </button>
                        </div>
                    `).join('') : '<div class="no-assignments">No assignments yet</div>'}
                </div>
            </div>
        </div>
    `;

    return div;
}

function toggleTimeSlot(header) {
    const content = header.nextElementSibling;
    const caret = header.querySelector('.time-slot-caret');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        caret.textContent = '▼';
    } else {
        content.style.display = 'none';
        caret.textContent = '▶';
    }
}


/* Get a scrollable list of MSDs, the current one highlighted, a badge showing how many sessions each has, click row to select, click the badge to see their schedule. */
function renderUsersMin() {
    /*Find the container */
    const container = document.getElementById('users-container');

    /* If users is empty, it shows a “No MSDs loaded yet” message with an “Add First MSD” button. */
    if (users.length === 0) {
        container.innerHTML = '<div class="no-data">No MSDs loaded yet.<br><button class="btn" onclick="showAddUserModal()">Add First MSD</button></div>';
        return;
    }

    /* Rebuild the list from users */

        container.innerHTML = '';
        /* For each user create a <div class="user-item">: 
            Clicking the whole row calls selectUser(user) (which updates the selection and re-renders sessions/calendar).
            Inserts the user’s name and an email tooltip (purely presentational—your CSS controls the hover behavior).
            Assignment count badge - Computes how many sessions that user is assigned to via getUserAssignments(user.id).
            Creates a <span class="assignment-count">N</span>:
            Sets title tooltip.
            Clicking the badge calls showMSDAssignments(user.id, e) to open the modal of that user’s assigned sessions.
            (Inside showMSDAssignments you call event.stopPropagation() so clicking the badge does not also trigger the row’s selectUser click.)

            DOM insertion detail
            It writes most of the row with innerHTML (which includes an assignment-count-placeholder), then replaces that placeholder with the real, clickable badge node (assignmentSpan). 
            That’s just a safe way to attach the badge with a live click handler.
        */
        users.forEach(user => {
            const div = document.createElement('div');
            div.className = `user-item ${selectedUser && selectedUser.id === user.id ? 'selected' : ''}`;
            div.onclick = () => selectUser(user);

            const userAssignments = getUserAssignments(user.id);
            const assignmentCount = userAssignments.length;

            div.innerHTML = `
                <div class="user-info">
                    <div class="user-name">
                        ${user.name}
                        <span class="email-tooltip">${user.email}</span>
                    </div>
                </div>
                <div class="assignment-count-placeholder"></div>
            `;

            // Create assignment count element with click handler
            /* Adds has-assignments if N > 0 so you can style “non-zero” counts. */
            const assignmentSpan = document.createElement('span');
            assignmentSpan.className = `assignment-count ${assignmentCount > 0 ? 'has-assignments' : ''}`;
            assignmentSpan.textContent = assignmentCount;
            assignmentSpan.title = `${assignmentCount} session${assignmentCount !== 1 ? 's' : ''} assigned`;
            assignmentSpan.onclick = (e) => showMSDAssignments(user.id, e);

            // Replace placeholder with the actual assignment span
            const placeholder = div.querySelector('.assignment-count-placeholder');
            placeholder.replaceWith(assignmentSpan);

            container.appendChild(div);
        });
}

function toggleSessionCollapse(sessionId) {
    // Handle both session-item and grouped-session elements
    let sessionElement = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
    if (!sessionElement) {
        sessionElement = document.querySelector(`.grouped-session[data-session-id="${sessionId}"]`);
    }
    if (!sessionElement) return;

    // Handle both session-details and grouped-session-details
    let sessionDetails = sessionElement.querySelector('.session-details');
    if (!sessionDetails) {
        sessionDetails = sessionElement.querySelector('.grouped-session-details');
    }

    const collapseIndicator = sessionElement.querySelector('.collapse-indicator');

    if (sessionElement.classList.contains('collapsed')) {
        // Expand
        sessionElement.classList.remove('collapsed');
        sessionElement.classList.add('expanded');
        if (sessionDetails) sessionDetails.style.display = 'block';
        if (collapseIndicator) collapseIndicator.textContent = '📂';
    } else {
        // Collapse
        sessionElement.classList.remove('expanded');
        sessionElement.classList.add('collapsed');
        if (sessionDetails) sessionDetails.style.display = 'none';
        if (collapseIndicator) collapseIndicator.textContent = '📁';
    }
}

function selectUser(user) {
    // If clicking on the already selected user, deselect them
    if (selectedUser && selectedUser.id === user.id) {
        selectedUser = null;
        console.log(`🔍 DEBUG: User ${user.name} deselected`);
    } else {
        selectedUser = user;
        console.log(`🔍 DEBUG: selectUser called with user: ${user.name} (ID: ${user.id})`);
        console.log(`🔍 DEBUG: selectedUser is now:`, selectedUser);
    }

    // Force remove selected class from all user items first
    document.querySelectorAll('.user-item.selected').forEach(el => {
        el.classList.remove('selected');
    });

    renderUsersMin();
    renderSessions();
    renderCalendar();
    console.log(`🔍 DEBUG: renderSessions() and renderCalendar() called, calendar should now show assign buttons`);
    console.log(`Selected user: ${selectedUser ? selectedUser.name : 'None'}`);
}

async function toggleAssignment(sessionId, userId) {
   console.log(`Toggle assignment for session ${sessionId} and user ${userId}`);
   console.log('Current assignments:', assignments);

    if (!assignments[sessionId]) {
        assignments[sessionId] = [];
    }

    const index = assignments[sessionId].findIndex(id => idsEqual(id, userId));

    if (index === -1) {
        console.log('1130');
        // Check for duplicate assignment to same session (unless it's a poster session)
        let newSession = findSessionById(sessionId);
        const sessionType = newSession?.session_info?.type?.toLowerCase() || '';
        const isPosterSession = sessionType.includes('poster');

        if (!isPosterSession && assignments[sessionId] && assignments[sessionId].length > 0) {
            const existingUser = users.find(u => u.id === assignments[sessionId][0]);
            const shouldContinue = await showDuplicateAssignmentModal(
                existingUser?.name || 'Unknown',
                newSession?.session_info?.title || 'Unknown Session'
            );

            if (!shouldContinue) {
                console.log(`Assignment blocked - session ${sessionId} already has an MSD assigned`);
                return;
            }
        }

        // Check for time conflicts before assigning
        if (newSession && hasTimeConflict(userId, newSession)) {
            const conflictingSessions = getConflictingSessions(userId, newSession);
            const conflictList = conflictingSessions.map(s => s.session_info?.title || `Session ${s.session_id}`).join('\n• ');

            const shouldContinue = confirm(
                `⚠️ TIME CONFLICT DETECTED\n\n` +
                `This user is already assigned to overlapping session(s):\n• ${conflictList}\n\n` +
                `A person cannot be in two places at the same time.\n\n` +
                `Do you want to proceed anyway? (Not recommended)`
            );

            if (!shouldContinue) {
                console.log(`Assignment blocked due to time conflict for user ${userId} and session ${sessionId}`);
                return;
            }
        }

        assignments[sessionId].push(userId);
        console.log(`Assigned user ${userId} to session ${sessionId}`);

        // Auto-collapse session after assignment
        setTimeout(() => {
            let sessionElement = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
            if (!sessionElement) {
                sessionElement = document.querySelector(`.grouped-session[data-session-id="${sessionId}"]`);
            }
            if (sessionElement && !sessionElement.classList.contains('collapsed')) {
                toggleSessionCollapse(sessionId);
            }
        }, 100);
    } else {
        assignments[sessionId].splice(index, 1);
        console.log(`Removed user ${userId} from session ${sessionId}`);

        // Auto-expand session when assignment is removed
        setTimeout(() => {
            let sessionElement = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
            if (!sessionElement) {
                sessionElement = document.querySelector(`.grouped-session[data-session-id="${sessionId}"]`);
            }
            if (sessionElement && sessionElement.classList.contains('collapsed')) {
                toggleSessionCollapse(sessionId);
            }
        }, 100);
    }

    renderSessions();
    renderCalendar(); // Update calendar view when assignments change
    renderUsersMin();
    updateStats();
    saveToStorage();
}

function hasTimeConflict(userId, newSession) {
    const userSessions = getUserAssignments(userId);

    return userSessions.some(sessionId => {
        // Skip self-comparison with flexible matching
        if (sessionId === newSession.session_id ||
            sessionId == newSession.session_id ||
            String(sessionId) === String(newSession.session_id)) {
            return false;
        }

        // Try multiple matching strategies due to type mismatches
        let existingSession = sessions.find(s => s.session_id === sessionId);
        if (!existingSession) {
            existingSession = sessions.find(s => s.session_id == sessionId);
        }
        if (!existingSession) {
            existingSession = sessions.find(s => String(s.session_id) === String(sessionId));
        }

        if (!existingSession) {
            // Session not found - this is expected for poster sessions like P-752
            return false;
        }

        // Check for date/time overlap
        const existingDate = existingSession.schedule?.date;
        const existingTime = existingSession.schedule?.time;
        const newDate = newSession.schedule?.date;
        const newTime = newSession.schedule?.time;

        // If dates are different, no conflict
        if (existingDate !== newDate) {
            return false;
        }

        // If same date and same time, there's a conflict
        if (existingTime === newTime) {
            return true;
        }

        return false;
    });
}

function getConflictingSessions(userId, newSession) {
    const userSessions = getUserAssignments(userId);
    const conflicting = [];

    userSessions.forEach(sessionId => {
        if (sessionId === newSession.session_id) return;

        const existingSession = sessions.find(s => s.session_id == sessionId);
        if (!existingSession) return;

        const existingDate = existingSession.schedule?.date;
        const existingTime = existingSession.schedule?.time;
        const newDate = newSession.schedule?.date;
        const newTime = newSession.schedule?.time;

        if (existingDate === newDate && existingTime === newTime) {
            conflicting.push(existingSession);
        }
    });

    return conflicting;
}

function removeAssignment(sessionId, userId) {
    if (assignments[sessionId]) {
        // Handle both string and number user IDs
        const index = assignments[sessionId].findIndex(id =>
            id == userId || id === String(userId) || id === Number(userId)
        );
        if (index !== -1) {
            assignments[sessionId].splice(index, 1);

            // Clean up empty assignment arrays
            if (assignments[sessionId].length === 0) {
                delete assignments[sessionId];
            }

            console.log(`✅ Removed assignment: User ${userId} from Session ${sessionId}`);
            renderSessions();
            renderUsersMin();
            updateStats();
            saveToStorage();
        }
    }
}

function getUserAssignments(userId) {
    const userAssignments = Object.keys(assignments).filter(sessionId => {
        // Check both string and number versions of userId
        return assignments[sessionId].includes(userId) ||
                assignments[sessionId].includes(String(userId)) ||
                assignments[sessionId].includes(Number(userId));
    });

    // Debug logging disabled to prevent console spam

    return userAssignments;
}

function findSessionById(sessionId) {
    return sessions.find(s => s.session_id === sessionId || s.session_id == sessionId || String(s.session_id) === String(sessionId));
}

function getConflicts(userId, session) {
    // This could be enhanced to return detailed conflict information
    return [];
}

function showAddUserModal() {
    document.getElementById('user-modal').style.display = 'block';
    document.getElementById('user-name').focus();
}

function closeUserModal() {
    document.getElementById('user-modal').style.display = 'none';
    // Clear form
    document.getElementById('user-name').value = '';
    document.getElementById('user-email').value = '';
    document.getElementById('user-department').value = '';
    document.getElementById('user-role').selectedIndex = 0;
}

function saveUser() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    const department = document.getElementById('user-department').value.trim();
    const role = document.getElementById('user-role').value;

    if (!name || !email) {
        showErrorMessage('Name and email are required');
        return;
    }

    // Check for duplicate email
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
        showErrorMessage('A user with this email already exists');
        return;
    }

    // Create new user
    const newId = Math.max(...users.map(u => u.id), 0) + 1;
    const user = {
        id: newId,
        userId: newId,
        name: name,
        firstname: name.split(' ')[0],
        lastname: name.split(' ').slice(1).join(' ') || name.split(' ')[0],
        email: email,
        department: department,
        role: role,
        assignedDate: new Date().toISOString(),
        createdAt: new Date().toISOString()
    };

    users.push(user);
    renderUsersMin();
    updateStats();
    saveToStorage();
    closeUserModal();

    showSuccessMessage(`Added ${name} as ${role}`);
}

function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('date-filter').value = '';
    document.getElementById('type-filter').value = '';
    filteredSessions = [];
    filterSessions();
}

function updateStats() {
    document.getElementById('total-sessions').textContent = sessions.length;
    document.getElementById('total-users').textContent = users.length;

    const assignmentCount = Object.values(assignments).reduce((sum, arr) => sum + arr.length, 0);
    document.getElementById('total-assignments').textContent = assignmentCount;

    // Calculate conflicts (simplified)
    let conflictCount = 0;
    // This would need more sophisticated conflict detection
    document.getElementById('conflicts-count').textContent = conflictCount;

    // Populate filters after data is loaded
    if (sessions.length > 0) {
        populateDateFilter();
    }
}

// Calendar rendering functions - USING WORKING HTML VERSION
function renderCalendar() {
    const container = document.getElementById('calendar-container');
    const summary = document.getElementById('calendar-summary');

    if (sessions.length === 0) {
        container.innerHTML = '<div class="no-data">No sessions available for calendar view.</div>';
        summary.textContent = 'No data';
        return;
    }

    // Group sessions by date, then by time slot
    const sessionsByDate = {};
    sessions.forEach(session => {
        const date = session.schedule?.date;
        if (date) {
            if (!sessionsByDate[date]) {
                sessionsByDate[date] = {};
            }
            const time = session.schedule?.time || 'Time TBD';
            if (!sessionsByDate[date][time]) {
                sessionsByDate[date][time] = [];
            }
            sessionsByDate[date][time].push(session);
        }
    });

    // Sort dates chronologically
    const sortedDates = Object.keys(sessionsByDate).sort((a, b) => {
        const dateA = new Date(a);
        const dateB = new Date(b);
        if (!isNaN(dateA.getTime()) && !isNaN(dateB.getTime())) {
            return dateA - dateB;
        }
        return a.localeCompare(b);
    });

    if (sortedDates.length === 0) {
        container.innerHTML = '<div class="no-data">No sessions with dates available.</div>';
        summary.textContent = 'No scheduled sessions';
        return;
    }

    // Parse times for sorting
    const parseTime = (timeStr) => {
        if (!timeStr || timeStr === 'TBD' || timeStr === 'Time TBD') return 0;
        const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
        if (!match) return 0;
        let hours = parseInt(match[1]);
        const minutes = parseInt(match[2]);
        const period = match[3].toUpperCase();
        if (period === 'PM' && hours !== 12) hours += 12;
        if (period === 'AM' && hours === 12) hours = 0;
        return hours * 60 + minutes;
    };

    // Force container to NOT use CSS grid and let our inner div handle the layout
    container.style.display = 'block';
    container.style.gridTemplateColumns = 'none';

    // SIMPLE CSS GRID - 3 COLUMNS FULL WIDTH
    let calendarHTML = '<div style="display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; gap: 20px !important; width: 100% !important; padding: 20px !important; box-sizing: border-box !important;">';

    console.log('Sorted dates found:', sortedDates.length, sortedDates);

    sortedDates.forEach(date => {
        // console.log('Processing date:', date);

        // Handle different date formats
        let dateObj;
        if (date.includes(',')) {
            dateObj = new Date(date);
        } else {
            dateObj = new Date(date + 'T00:00:00');
        }

        let dayName, dayNumber;
        if (isNaN(dateObj.getTime())) {
            console.warn('Failed to parse date:', date);
            dayName = date.split(',')[0] || 'Unknown Day';
            dayNumber = date.split(' ')[2] || '?';
        } else {
            dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
            dayNumber = dateObj.getDate();
        }

        // Sort time slots chronologically
        const timeSlots = Object.keys(sessionsByDate[date]).sort((a, b) => {
            return parseTime(a) - parseTime(b);
        });

        calendarHTML += `
            <div style="border: 1px solid #ddd; border-radius: 8px; background: white; overflow: hidden; display: flex; flex-direction: column; max-height: 70vh;">
                <div style="background: #343a40; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px;">
                    ${dayName} ${dayNumber}
                </div>
                <div style="padding: 15px; overflow-y: auto; flex: 1;">
        `;

        timeSlots.forEach((timeSlot, index) => {
            const sessionsInSlot = sessionsByDate[date][timeSlot];
            const sessionCount = sessionsInSlot.length;
            const assignedCount = sessionsInSlot.filter(session =>
                assignments[getSessionId(session)] && assignments[getSessionId(session)].length > 0
            ).length;

            calendarHTML += `
                <div class="alert alert-secondary py-2 mb-2">
                    <div class="fw-bold">${timeSlot}</div>
                    <small class="text-muted">
                        ${sessionCount} session${sessionCount !== 1 ? 's' : ''}
                        ${assignedCount > 0 ? `• ${assignedCount} assigned` : ''}
                    </small>
                </div>
            `;

            // Add individual sessions under the time slot
            sessionsInSlot.forEach(session => {
                const sessionAssignments = assignments[getSessionId(session)] || [];
                const assignedUsers = sessionAssignments.map(userId =>
                    users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId))
                ).filter(Boolean);
                const hasAssignments = assignedUsers.length > 0;
                const title = getSessionTitle(session);
                const location = session.schedule?.location || 'TBD';
                const sessionId = getSessionId(session);

                calendarHTML += `
                    <div class="card mb-2 calendar-session ${hasAssignments ? 'assigned border-primary' : 'unassigned border-warning'}"
                         data-session-id="${sessionId}"
                         title="${title} - ${location}">
                        <div class="card-body p-2">
                            <div class="fw-semibold" style="font-size: 14px;">
                                ${title.length > 60 ? title.substring(0, 60) + '...' : title}
                            </div>
                            <div style="display: flex !important; justify-content: space-between !important; align-items: center !important; margin-top: 0.25rem; width: 100%;">
                                <small style="color: #6c757d; margin: 0;">📍 ${location}</small>
                                ${assignedUsers.length > 0 ?
                                    `<small style="font-weight: bold; color: #198754; margin: 0; text-align: right;">${assignedUsers.map(u => (u.name || u.firstname || 'Unknown').split(' ')[0]).join(', ')}</small>` :
                                    '<small style="color: #6c757d; margin: 0; text-align: right;">⚪ Unassigned</small>'
                                }
                            </div>
                            ${selectedUser ? `
                                <div class="mt-2 pt-2 border-top">
                                    ${sessionAssignments.some(id => id == selectedUser.id) ? `
                                    <button class="btn btn-sm btn-danger"
                                            onclick="toggleAssignment('${sessionId}', ${selectedUser.id}); event.stopPropagation();">
                                        ➖ Unassign
                                    </button>
                                    ` : `
                                    <button class="btn btn-sm btn-success"
                                            onclick="toggleAssignment('${sessionId}', ${selectedUser.id}); event.stopPropagation();">
                                        📌 Assign
                                    </button>
                                    `}
                                </div>
                                ` : `
                               <div class="mt-2 pt-2 border-top">
                                   
                                </div>
                                `}

                        </div>
                    </div>
                `;
            });
        });

        calendarHTML += '</div></div>'; // Close day content and day column
    });

    calendarHTML += '</div>'; // Close CSS grid
    container.innerHTML = calendarHTML;

    const assignedCount = sessions.filter(s => assignments[getSessionId(s)]?.length > 0).length;
    summary.textContent = `${assignedCount}/${sessions.length} sessions assigned`;
}

// Function to make calendar responsive to screen width changes
function makeCalendarResponsive(calendarGrid) {
    function updateCalendarLayout() {
        const containerWidth = calendarGrid.parentElement?.offsetWidth || window.innerWidth;

        // Adjust columns based on available width
        if (containerWidth < 768) {
            // Mobile: 1 column
            calendarGrid.style.gridTemplateColumns = 'repeat(1, 1fr)';
            calendarGrid.style.gap = '15px';
            calendarGrid.style.padding = '15px';
        } else if (containerWidth < 1200) {
            // Tablet: 2 columns with smaller gap
            calendarGrid.style.gridTemplateColumns = 'repeat(2, minmax(250px, 1fr))';
            calendarGrid.style.gap = '15px';
            calendarGrid.style.padding = '15px';
        } else {
            // Desktop: 2 columns with full responsiveness
            calendarGrid.style.gridTemplateColumns = 'repeat(2, minmax(300px, 1fr))';
            calendarGrid.style.gap = '20px';
            calendarGrid.style.padding = '20px';
        }
    }

    // Update layout immediately
    updateCalendarLayout();

    // Add resize listener for future changes
    window.addEventListener('resize', updateCalendarLayout);
}

function scrollToSession(sessionId) {
    const sessionElements = document.querySelectorAll('.session-item');
    sessionElements.forEach(element => {
        if (element.dataset.sessionId === sessionId) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.style.boxShadow = '0 0 10px rgba(44, 90, 160, 0.5)';
            setTimeout(() => {
                element.style.boxShadow = '';
            }, 2000);
        }
    });
}

function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));

    // Show selected tab content
    const selectedTabContent = document.getElementById(tabName + '-tab-content');
    const selectedTabButton = document.getElementById(tabName + '-tab');

    if (selectedTabContent && selectedTabButton) {
        selectedTabContent.classList.add('active');
        selectedTabButton.classList.add('active');

        // If switching to calendar tab, refresh the calendar display
        if (tabName === 'calendar') {
            renderCalendar();
        }
    }
}


function exportAssignments() {
    const exportData = {
        exportInfo: {
            tool: 'IDWeek 2025 Attendance Assignments',
            exportDate: new Date().toISOString(),
            sessionCount: sessions.length,
            userCount: users.length,
            assignmentCount: Object.values(assignments).reduce((sum, arr) => sum + arr.length, 0)
        },
        sessions: sessions,
        users: users,
        assignments: assignments
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `idweek2025_assignments_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showSuccessMessage('Assignment data exported successfully!');
}

function generateReports() {
    if (users.length === 0) {
        showErrorMessage('No users to generate reports for');
        return;
    }

    let report = 'IDWeek 2025 - Assignment Report\n';
    report += '='.repeat(50) + '\n';
    report += `Generated: ${new Date().toLocaleDateString()}\n`;
    report += `Sessions: ${sessions.length} | Users: ${users.length} | Assignments: ${Object.values(assignments).reduce((sum, arr) => sum + arr.length, 0)}\n\n`;

    // User schedules
    report += 'INDIVIDUAL SCHEDULES\n';
    report += '-'.repeat(30) + '\n\n';

    users.forEach(user => {
        const userSessions = getUserAssignments(user.id)
            .map(sessionId => sessions.find(s => s.session_id === sessionId))
            .filter(Boolean)
            .sort((a, b) => {
                const dateA = new Date(a.schedule?.date || '2025-01-01');
                const dateB = new Date(b.schedule?.date || '2025-01-01');
                return dateA - dateB;
            });

        report += `${user.name} (${user.email})\n`;
        if (user.department) report += `${user.department}\n`;
        report += `Role: ${user.role}\n`;
        report += `Sessions: ${userSessions.length}\n\n`;

        if (userSessions.length === 0) {
            report += '  No sessions assigned\n\n';
        } else {
            userSessions.forEach(session => {
                report += `  • ${session.session_info?.title || 'Untitled'}\n`;
                report += `    ${formatDate(session.schedule?.date)} | ${session.schedule?.time || 'TBD'}\n`;
                report += `    📍 ${session.schedule?.location || 'TBD'}\n\n`;
            });
        }

        report += '\n';
    });

    // Session attendance
    report += '\n\nSESSION ATTENDANCE\n';
    report += '-'.repeat(30) + '\n\n';

    const sessionsWithAttendees = sessions.filter(session =>
        assignments[getSessionId(session)] && assignments[getSessionId(session)].length > 0
    ).sort((a, b) => {
        const dateA = new Date(a.schedule?.date || '2025-01-01');
        const dateB = new Date(b.schedule?.date || '2025-01-01');
        return dateA - dateB;
    });

    sessionsWithAttendees.forEach(session => {
        const sessionAssignments = assignments[getSessionId(session)] || [];
        const assignedUsers = sessionAssignments.map(userId =>
            users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId))
        ).filter(Boolean).sort((a, b) => {
            // Sort by lastname alphabetically
            const lastNameA = a.lastname || a.name?.split(' ').pop() || '';
            const lastNameB = b.lastname || b.name?.split(' ').pop() || '';
            return lastNameA.localeCompare(lastNameB);
        });

        report += `${session.session_info?.title || 'Untitled'}\n`;
        report += `${formatDate(session.schedule?.date)} | ${session.schedule?.time || 'TBD'}\n`;
        report += `📍 ${session.schedule?.location || 'TBD'}\n`;
        report += `Attendees (${assignedUsers.length}):\n`;

        assignedUsers.forEach(user => {
            report += `  • ${user.name} (${user.email}) - ${user.role}\n`;
        });

        report += '\n';
    });

    // Download report
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `idweek2025_report_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showSuccessMessage('Report generated and downloaded!');
}

function forceReload() {
    console.log('🔄 Force reloading all data from database...');
    // Clear cached data
    users = [];
    assignments = {};
    selectedUser = null;
    // Clear localStorage
    localStorage.removeItem('idweek2025_tool_data');
    // Force reload from database
    loadMSDData();
    showSuccessMessage('Data reloaded from database');
}

function clearAllData() {
    if (confirm('⚠️ This will remove ALL users and assignments. Are you sure?')) {
        users = [];
        assignments = {};
        selectedUser = null;
        localStorage.removeItem('idweek2025_tool_data');
        renderUsersMin();
        renderSessions();
        updateStats();
        // Trigger MSD data reload
        loadMSDData();
        showSuccessMessage('All data cleared - MSDs will reload automatically');
    }
}

function saveToStorage() {
    // Save assignments to database
    const assignmentData = Object.keys(assignments).map(sessionId =>
        assignments[sessionId].map(userId => ({
            session_id: sessionId,
            user_id: userId
        }))
    ).flat();

    console.log('💾 Saving assignments to database:', {
        conferenceId: getConferenceId(),
        assignmentCount: assignmentData.length,
        assignments: assignmentData
    });

    // Save to database
    saveToDatabase();
}

function saveToDatabase() {
    console.log('💾 Attempting to save to database...');

    fetch(apiUrl('api_save.cfm'), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conferenceId: 1, // IDWeek 2025 conference ID
            assignments: JSON.stringify(assignments) // Double-stringify for ColdFusion
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('✅ Successfully saved assignments to database:', data);
            showSuccessMessage(`Saved ${data.assignmentCount} assignments to database!`);
        } else {
            if (data.fallback) {
                console.log('⚠️ Database not configured:', data.error);
                console.log('⚠️ Using localStorage until database is set up');
            } else {
                console.error('❌ Database save failed:', data.error);
                console.log('⚠️ Falling back to localStorage...');
            }
            saveToLocalStorage();
        }
    })
    .catch(error => {
        console.error('❌ Database API error:', error);
        console.log('⚠️ Database API not available, using localStorage fallback');
        saveToLocalStorage();
    });
}

function saveToLocalStorage() {

    // Save to localStorage immediately
    try {
        const storageData = {
            assignments: assignments,
            users: users,
            selectedUserId: selectedUser?.id,
            exportDate: new Date().toISOString(),
            conferenceId: getConferenceId()
        };
        localStorage.setItem('conference_assignments', JSON.stringify(storageData));
        console.log('✅ Successfully saved assignments to localStorage');
        return;
    } catch (error) {
        console.error('❌ Error saving to localStorage:', error);
    }

    // Database save code (commented out until API is fixed)
    /*
    fetch(apiUrl('api_assignments.cfm'), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            confid: getConferenceId(),
            assignments: assignmentData
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Successfully saved assignments to database:', data);
    })
    .catch(error => {
        console.error('❌ Error saving assignments to database:', error);
    });
    */
}

function loadStoredData() {
    // Load assignments from database
    console.log('📥 Loading assignments from database for conference ID:', getConferenceId());
    fetch(apiUrl(`api_assignments.cfm?confid=${getConferenceId()}`))
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Loaded assignments from database:', data);
            console.log('🔍 Raw assignments data:', data.assignments);

            // Convert database format to frontend format (merge with existing, don't replace)
            if (data.assignments && Object.keys(data.assignments).length > 0) {
                console.log('🔄 Merging database assignments with existing assignments');
                assignments = {...assignments, ...data.assignments}; // Merge instead of replace
            }

            console.log('🔍 Processed assignments object:', assignments);
            console.log('🔍 Assignment keys:', Object.keys(assignments));
            console.log('🔍 Sample assignment:', Object.keys(assignments).length > 0 ? assignments[Object.keys(assignments)[0]] : 'none');

            const assignmentCount = Object.values(assignments).reduce((sum, arr) => sum + arr.length, 0);
            console.log(`📊 Assignment summary: ${Object.keys(assignments).length} sessions with ${assignmentCount} total assignments`);

            if (users.length > 0) {
                console.log(`Using ${users.length} MSDs, loaded ${assignmentCount} assignments from database`);
                // Force re-render to show assignment counts in left panel
                renderUsersMin();
                updateStats();
                renderSessions();
                // Re-render users again to ensure assignment counts are displayed
                setTimeout(() => {
                    console.log('🔄 Re-rendering users to show assignment counts...');
                    renderUsersMin();
                    updateStats();
                    // TEMPORARILY DISABLED: Ensure assigned sessions are properly collapsed after data loads
                    console.log('🔧 DISABLED: Session collapse logic to fix display issue');
                    // Object.keys(assignments).forEach(sessionId => {
                    //     if (assignments[sessionId].length > 0) {
                    //         console.log('🔍 Looking for session element with ID:', sessionId);
                    //         let sessionElement = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
                    //         if (!sessionElement) {
                    //             sessionElement = document.querySelector(`.grouped-session[data-session-id="${sessionId}"]`);
                    //         }
                    //         console.log('🔍 Found session element:', !!sessionElement);
                    //         if (sessionElement && !sessionElement.classList.contains('collapsed')) {
                    //             sessionElement.classList.add('collapsed');
                    //             sessionElement.classList.remove('expanded');
                    //             let sessionDetails = sessionElement.querySelector('.session-details');
                    //             if (!sessionDetails) {
                    //                 sessionDetails = sessionElement.querySelector('.grouped-session-details');
                    //             }
                    //             const collapseIndicator = sessionElement.querySelector('.collapse-indicator');
                    //             if (sessionDetails) sessionDetails.style.display = 'none';
                    //             if (collapseIndicator) collapseIndicator.textContent = '📁';
                    //         }
                    //     }
                    // });
                }, 100);
                if (assignmentCount > 0) {
                    showSuccessMessage(`Loaded ${assignmentCount} assignments from database`);
                }
            }
        })
        .catch(error => {
            console.error('Error loading assignments from database:', error);
            console.log('Falling back to localStorage...');

            // Fallback to localStorage
            try {
                const stored = localStorage.getItem('conference_assignments');
                if (stored) {
                    const data = JSON.parse(stored);

                    // Load assignments (preserve existing assignments, don't overwrite completely)
                    if (data.assignments && Object.keys(data.assignments).length > 0) {
                        console.log('🔄 Merging localStorage assignments with existing assignments');
                        assignments = {...assignments, ...data.assignments}; // Merge instead of replace
                    }

                    // Only override users if we don't already have MSDs loaded
                    if (users.length === 0 && data.users && data.users.length > 0) {
                        users = data.users;
                        console.log(`Loaded ${users.length} users from localStorage fallback`);
                        renderUsersMin();
                        updateStats();
                    } else if (users.length > 0) {
                        // We have MSDs loaded, just update assignments and re-render
                        console.log(`Using ${users.length} MSDs, loading ${Object.keys(assignments).length} assignments from localStorage fallback`);
                        if (data.selectedUserId) {
                            selectedUser = users.find(u => u.id === data.selectedUserId);
                        }
                        renderUsersMin();
                        renderSessions();
                        updateStats();
                        // Ensure assigned sessions are properly collapsed after localStorage load
                        setTimeout(() => {
                            Object.keys(assignments).forEach(sessionId => {
                                if (assignments[sessionId].length > 0) {
                                    let sessionElement = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
                                    if (!sessionElement) {
                                        sessionElement = document.querySelector(`.grouped-session[data-session-id="${sessionId}"]`);
                                    }
                                    if (sessionElement && !sessionElement.classList.contains('collapsed')) {
                                        sessionElement.classList.add('collapsed');
                                        sessionElement.classList.remove('expanded');
                                        let sessionDetails = sessionElement.querySelector('.session-details');
                                        if (!sessionDetails) {
                                            sessionDetails = sessionElement.querySelector('.grouped-session-details');
                                        }
                                        const collapseIndicator = sessionElement.querySelector('.collapse-indicator');
                                        if (sessionDetails) sessionDetails.style.display = 'none';
                                        if (collapseIndicator) collapseIndicator.textContent = '📁';
                                    }
                                }
                            });
                        }, 100);
                    }
                }
            } catch (localError) {
                console.error('Error loading from localStorage fallback:', localError);
            }

            // Final fallback: ensure sessions are rendered even if assignments fail to load
            console.log('🔧 Final fallback: rendering sessions with no assignments');
            if (sessions.length > 0) {
                renderSessions();
                updateStats();
            }
        });
}

// Modal functions
function showAttendeesBySession() {
    console.log('🔍 showAttendeesBySession called - sessions:', sessions.length, 'users:', users.length);
    if (sessions.length === 0) {
        showErrorMessage('No sessions loaded yet');
        return;
    }

    const modal = document.getElementById('attendees-by-session-modal');
    console.log('🔍 Modal element found:', !!modal);
    if (modal) {
        modal.style.display = 'block';
        renderAttendeesBySession();
    } else {
        console.error('❌ attendees-by-session-modal not found');
    }

    // Add search functionality
    document.getElementById('session-search').oninput = function() {
        renderAttendeesBySession(this.value.toLowerCase());
    };
}

function closeAttendeesBySessionModal() {
    document.getElementById('attendees-by-session-modal').style.display = 'none';
}

function renderAttendeesBySession(searchTerm = '') {
    const container = document.getElementById('attendees-by-session-content');

    // Get sessions with assignments
    const sessionsWithAssignments = sessions.filter(session => {
        const sessionId = getSessionId(session);
        const sessionAssignments = assignments[sessionId] || [];

        if (sessionAssignments.length === 0) return false;

        if (searchTerm) {
            const title = getSessionTitle(session).toLowerCase();
            const location = session.schedule?.location?.toLowerCase() || '';
            return title.includes(searchTerm) || location.includes(searchTerm);
        }

        return true;
    }).sort((a, b) => {
        // Sort by date, then time
        const dateA = new Date(a.schedule?.date || '2025-01-01');
        const dateB = new Date(b.schedule?.date || '2025-01-01');
        if (dateA.getTime() !== dateB.getTime()) {
            return dateA - dateB;
        }
        return (a.schedule?.time || '').localeCompare(b.schedule?.time || '');
    });

    if (sessionsWithAssignments.length === 0) {
        container.innerHTML = '<div class="no-data">No assigned sessions found</div>';
        return;
    }

    let html = '';
    sessionsWithAssignments.forEach(session => {
        const sessionId = getSessionId(session);
        const sessionAssignments = assignments[sessionId] || [];
        const assignedUsers = sessionAssignments.map(userId =>
            users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId))
        ).filter(Boolean);

        html += `
            <div class="session-assignment-item">
                <div class="session-info">
                    <h4>${getSessionTitle(session)}</h4>
                    <div class="session-details">
                        <span>📅 ${formatDate(session.schedule?.date)}</span>
                        <span>🕐 ${session.schedule?.time || 'TBD'}</span>
                        <span>📍 ${session.schedule?.location || 'TBD'}</span>
                    </div>
                </div>
                <div class="attendees-list">
                    <h5>Assigned MSDs (${assignedUsers.length}):</h5>
                    ${assignedUsers.map(user => `
                        <div class="attendee-item">
                            <span class="user-name">${user.name}</span>
                            <span class="user-details">${user.email}</span>
                            <button class="btn btn-sm btn-danger" onclick="removeAssignment('${sessionId}', ${user.id}); renderAttendeesBySession();">
                                Remove
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function showSessionsByAttendee() {
    console.log('🔍 showSessionsByAttendee called - sessions:', sessions.length, 'users:', users.length);
    if (users.length === 0) {
        showErrorMessage('No attendees added yet');
        return;
    }

    const modal = document.getElementById('sessions-by-attendee-modal');
    console.log('🔍 Modal element found:', !!modal);
    if (modal) {
        modal.style.display = 'block';
        renderSessionsByAttendee();
    } else {
        console.error('❌ sessions-by-attendee-modal not found');
    }

    // Add search functionality
    document.getElementById('attendee-search').oninput = function() {
        renderSessionsByAttendee(this.value.toLowerCase());
    };
}

function closeSessionsByAttendeeModal() {
    document.getElementById('sessions-by-attendee-modal').style.display = 'none';
}

function renderSessionsByAttendee(searchTerm = '') {
    const container = document.getElementById('sessions-by-attendee-content');

    // Filter and sort users
    let filteredUsers = users;
    if (searchTerm) {
        filteredUsers = users.filter(user =>
            user.name.toLowerCase().includes(searchTerm) ||
            user.email.toLowerCase().includes(searchTerm) ||
            (user.department && user.department.toLowerCase().includes(searchTerm))
        );
    }

    filteredUsers.sort((a, b) => a.name.localeCompare(b.name));

    if (filteredUsers.length === 0) {
        container.innerHTML = '<div class="no-data">No attendees found</div>';
        return;
    }

    let html = '';
    filteredUsers.forEach(user => {
        const userSessions = getUserAssignments(user.id)
            .map(sessionId => sessions.find(s => getSessionId(s) === sessionId))
            .filter(Boolean)
            .sort((a, b) => {
                const dateA = new Date(a.schedule?.date || '2025-01-01');
                const dateB = new Date(b.schedule?.date || '2025-01-01');
                return dateA - dateB;
            });

        html += `
            <div class="attendee-assignment-item">
                <div class="attendee-info">
                    <h4>${user.name}</h4>
                    <div class="attendee-details">
                        <span>📧 ${user.email}</span>
                        ${user.department ? `<span>🏢 ${user.department}</span>` : ''}
                    </div>
                </div>
                <div class="sessions-list">
                    <h5>Assigned Sessions (${userSessions.length}):</h5>
                    ${userSessions.length === 0 ? '<div class="no-assignments">No sessions assigned</div>' : ''}
                    ${userSessions.map(session => `
                        <div class="session-item-small">
                            <div class="session-basic-info">
                                <span class="session-title">${getSessionTitle(session)}</span>
                                <br><span style="font-size: 12px; color: #666;">${user.email}</span>
                                ${user.department ? `<br><span style="font-size: 12px; color: #666;">${user.department}</span>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function showMSDAssignments(userId, event) {
    event.stopPropagation(); // Prevent user selection when clicking assignment count

    const user = users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId));
    if (!user) return;

    const modal = document.getElementById('msd-assignments-modal');
    const title = document.getElementById('msd-assignments-title');
    const content = document.getElementById('msd-assignments-content');

    const userSessionIds = getUserAssignments(user.id);

    title.textContent = `${user.name} - Total Assignments: ${userSessionIds.length}`;
    console.log(`🔍 DEBUG showMSDAssignments for user ${user.id}:`, {
        userName: user.name,
        userSessionIds: userSessionIds,
        userSessionIdsTypes: userSessionIds.map(id => ({id, type: typeof id})),
        allAssignments: assignments,
        sessionsTotal: sessions.length,
        sampleSessionIds: sessions.slice(0, 5).map(s => ({
            session_id: s.session_id,
            session_id_type: typeof s.session_id,
            getSessionId: getSessionId(s),
            getSessionId_type: typeof getSessionId(s),
            title: getSessionTitle(s)
        }))
    });

    const userSessions = userSessionIds
        .map((sessionId, index) => {
            console.log(`🔍 Searching for session ${index + 1}/${userSessionIds.length}: ID="${sessionId}" (type: ${typeof sessionId})`);

            // Try multiple matching strategies
            let session = sessions.find(s => s.session_id === sessionId);
            if (!session) session = sessions.find(s => s.session_id == sessionId);
            if (!session) session = sessions.find(s => String(s.session_id) === String(sessionId));
            if (!session) session = sessions.find(s => getSessionId(s) === sessionId);
            if (!session) session = sessions.find(s => getSessionId(s) == sessionId);

            if (!session) {
                console.log(`❌ Could not find session for ID: ${sessionId} (type: ${typeof sessionId})`);
                console.log(`   Available session IDs:`, sessions.slice(0, 10).map(s => `"${s.session_id}" (${typeof s.session_id})`));
                console.log(`   Available getSessionId results:`, sessions.slice(0, 10).map(s => `"${getSessionId(s)}" (${typeof getSessionId(s)})`));

                // Create a placeholder session for missing assignments
                return {
                    session_id: sessionId,
                    id: sessionId,
                    session_info: { title: `Missing Session (${sessionId})` },
                    schedule: { date: '2025-10-20', time: 'TBD', location: 'TBD' },
                    tracks: { primary_track: 'Unknown' },
                    _missing: true
                };
            } else {
                console.log(`✅ Found session: ${getSessionTitle(session)}`);
            }
            return session;
        })
        .filter(Boolean)
        .sort((a, b) => {
            const dateA = new Date(a.schedule?.date || '2025-01-01');
            const dateB = new Date(b.schedule?.date || '2025-01-01');
            return dateA - dateB;
        });

    if (userSessions.length === 0) {
        content.innerHTML = '<div class="no-data">No sessions assigned to this MSD</div>';
    } else {
        /* let html = `
            <div class="msd-info-summary">
                <h4>${user.name}</h4>
                <p><strong>Email:</strong> ${user.email}</p>
                ${user.department ? `<p><strong>Department:</strong> ${user.department}</p>` : ''}
                <p><strong>Role:</strong> ${user.role}</p>
                <p><strong>Total Assignments:</strong> ${userSessions.length}</p>
            </div>
            <hr>
            <h4>Assigned Sessions:</h4>
        `; */
        let html = ``;


        // Group by date
        const sessionsByDate = new Map();
        userSessions.forEach(session => {
            const date = session.schedule?.date || 'TBD';
            if (!sessionsByDate.has(date)) {
                sessionsByDate.set(date, []);
            }
            sessionsByDate.get(date).push(session);
        });

        // Sort dates
        const sortedDates = Array.from(sessionsByDate.keys()).sort((a, b) => {
            if (a === 'TBD') return 1;
            if (b === 'TBD') return -1;
            return new Date(a) - new Date(b);
        });

        sortedDates.forEach(date => {
            const dateSessions = sessionsByDate.get(date);
            html += `
                <div class="date-group-assignments">
                    <h5>📅 ${formatDate(date)} (${dateSessions.length} session${dateSessions.length !== 1 ? 's' : ''})</h5>
                    ${dateSessions.map(session => `
                        <div class="session-card ${session._missing ? 'missing-session' : ''}">
                            <div class="session-card-content">
                                <div class="session-title">
                                    ${session._missing ? '⚠️ ' : ''}${getSessionTitle(session)}
                                    ${session._missing ? ' <span class="missing-badge">Data Not Found</span>' : ''}
                                </div>
                                <div class="session-meta">
                                    <div class="date-time">🕐 ${session.schedule?.time || 'TBD'} • <span class="session-type-inline">${session.session_info?.type || 'General'}</span></div>
                                    <div class="location">📍 ${session.schedule?.location || 'TBD'}</div>
                                </div>
                            </div>
                            <button class="btn-remove"
                                    onclick="removeAssignmentFromModal('${getSessionId(session)}', ${user.id})">
                                Remove
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        });

        content.innerHTML = html;
    }

    modal.style.display = 'block';
}

function removeAssignmentFromModal(sessionId, userId) {
    if (assignments[sessionId]) {
        const index = assignments[sessionId].findIndex(id =>
            id == userId || id === String(userId) || id === Number(userId)
        );
        if (index !== -1) {
            assignments[sessionId].splice(index, 1);
            if (assignments[sessionId].length === 0) {
                delete assignments[sessionId];
            }

            console.log(`✅ Removed assignment: User ${userId} from Session ${sessionId}`);
            renderUsersMin();
            renderSessions();
            updateStats();
            saveToStorage();

            // Re-open the modal to show updated assignments
            const user = users.find(u => u.id == userId || u.id === String(userId) || u.id === Number(userId));
            if (user) {
                showMSDAssignments(user.id, { stopPropagation: () => {} });
            }
        }
    }
}

function closeMSDAssignmentsModal() {
    document.getElementById('msd-assignments-modal').style.display = 'none';
}

// Utility functions
function showSuccessMessage(message) {
    // Simple success notification - could be enhanced with a toast library
    console.log('✅ SUCCESS:', message);

    // Create temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 5px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

function showErrorMessage(message) {
    // Simple error notification
    console.error('❌ ERROR:', message);

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 12px 20px;
        border-radius: 5px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function showDuplicateAssignmentModal(existingUserName, sessionTitle) {
    return new Promise((resolve) => {
        const shouldContinue = confirm(
            `⚠️ DUPLICATE ASSIGNMENT\n\n` +
            `This session already has an MSD assigned:\n` +
            `• ${existingUserName}\n\n` +
            `Session: ${sessionTitle}\n\n` +
            `Do you want to assign another MSD to the same session?\n` +
            `(This will result in multiple MSDs attending the same session)`
        );
        resolve(shouldContinue);
    });
}

function idsEqual(a, b) {
  return String(a) === String(b);
}

function isUserAssignedToSession(sessionId, userId) {
  const arr = assignments[sessionId] || [];
  return arr.some(id => idsEqual(id, userId));
}

// Test function to verify JavaScript is loading
function testJavaScript() {
    console.log('🧪 TEST: JavaScript is working!');
    alert('JavaScript is working!');
}

// Make modal functions globally accessible for onclick handlers
window.showAttendeesBySession = showAttendeesBySession;
window.showSessionsByAttendee = showSessionsByAttendee;
window.testJavaScript = testJavaScript;

console.log('🚀 JavaScript file loaded completely');
console.log('Functions available:', {
    showAttendeesBySession: typeof window.showAttendeesBySession,
    showSessionsByAttendee: typeof window.showSessionsByAttendee,
    testJavaScript: typeof window.testJavaScript
});