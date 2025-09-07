/**
 * IDWeek 2025 PWA - Main Application Controller
 * Manages the overall application state, routing, and user interactions
 */

class IDWeekApp {
    constructor() {
        this.sessions = [];
        this.filteredSessions = [];
        this.bookmarkedSessions = new Set();
        this.currentView = 'sessions';
        this.filterState = {
            search: '',
            date: '',
            priority: '',
            tags: new Set()
        };
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing IDWeek 2025 PWA...');
        
        // Load data
        await this.loadSessionData();
        
        // Initialize UI components
        this.initializeUI();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load user preferences
        this.loadUserPreferences();
        
        // Render initial view
        this.renderSessions();
        
        console.log('✅ Application initialized successfully');
    }
    
    async loadSessionData() {
        try {
            // Try to load from cache first (offline support)
            const cachedData = this.getCachedData();
            if (cachedData) {
                this.sessions = cachedData;
                console.log('📱 Loaded from cache:', this.sessions.length, 'sessions');
            }
            
            // Try to fetch fresh data
            if (navigator.onLine) {
                try {
                    const response = await fetch('../batch1_firecrawl_validated.json');
                    if (response.ok) {
                        const freshData = await response.json();
                        this.sessions = freshData;
                        this.cacheData(freshData);
                        console.log('🌐 Loaded fresh data:', this.sessions.length, 'sessions');
                    }
                } catch (error) {
                    console.warn('⚠️ Failed to fetch fresh data, using cache:', error);
                }
            }
            
            this.filteredSessions = [...this.sessions];
            this.updateStats();
            this.populateTagFilters();
            
        } catch (error) {
            console.error('❌ Error loading session data:', error);
            this.showErrorMessage('Failed to load session data. Please try again.');
        }
    }
    
    getCachedData() {
        try {
            const cached = localStorage.getItem('idweek2025_sessions');
            return cached ? JSON.parse(cached) : null;
        } catch (error) {
            console.warn('⚠️ Error reading cache:', error);
            return null;
        }
    }
    
    cacheData(data) {
        try {
            localStorage.setItem('idweek2025_sessions', JSON.stringify(data));
            localStorage.setItem('idweek2025_cache_timestamp', Date.now().toString());
        } catch (error) {
            console.warn('⚠️ Error caching data:', error);
        }
    }
    
    initializeUI() {
        // Initialize tab navigation
        this.setupTabNavigation();
        
        // Initialize floating action button
        this.setupFloatingActionButton();
        
        // Initialize modal handlers
        this.setupModalHandlers();
        
        // Check connection status
        this.updateConnectionStatus();
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');
        
        searchInput?.addEventListener('input', this.debounce((e) => {
            this.filterState.search = e.target.value;
            this.applyFilters();
        }, 300));
        
        clearSearch?.addEventListener('click', () => {
            searchInput.value = '';
            this.filterState.search = '';
            this.applyFilters();
        });
        
        // Filter dropdowns
        const dateFilter = document.getElementById('dateFilter');
        const priorityFilter = document.getElementById('priorityFilter');
        
        dateFilter?.addEventListener('change', (e) => {
            this.filterState.date = e.target.value;
            this.applyFilters();
        });
        
        priorityFilter?.addEventListener('change', (e) => {
            this.filterState.priority = e.target.value;
            this.applyFilters();
        });
        
        // Connection status monitoring
        window.addEventListener('online', () => this.updateConnectionStatus());
        window.addEventListener('offline', () => this.updateConnectionStatus());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        searchInput?.focus();
                        break;
                    case 'b':
                        e.preventDefault();
                        this.switchView('bookmarks');
                        break;
                }
            }
        });
    }
    
    setupTabNavigation() {
        const tabLinks = document.querySelectorAll('[data-tab]');
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = e.currentTarget.dataset.tab;
                this.switchView(tab);
            });
        });
    }
    
    setupFloatingActionButton() {
        const fabMenu = document.getElementById('fabMenu');
        const fabOptions = document.getElementById('fabOptions');
        
        fabMenu?.addEventListener('click', () => {
            fabOptions?.classList.toggle('active');
        });
        
        // FAB option handlers
        document.getElementById('exportData')?.addEventListener('click', () => this.exportData());
        document.getElementById('syncData')?.addEventListener('click', () => this.syncData());
        document.getElementById('shareApp')?.addEventListener('click', () => this.shareApp());
    }
    
    setupModalHandlers() {
        // Modal event delegation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-session-id]') || e.target.closest('[data-session-id]')) {
                const sessionElement = e.target.closest('[data-session-id]');
                const sessionId = sessionElement.dataset.sessionId;
                this.showSessionDetails(sessionId);
            }
            
            if (e.target.matches('.bookmark-btn') || e.target.closest('.bookmark-btn')) {
                e.preventDefault();
                e.stopPropagation();
                const sessionElement = e.target.closest('[data-session-id]');
                const sessionId = sessionElement.dataset.sessionId;
                this.toggleBookmark(sessionId);
            }
        });
        
        // Modal action buttons
        document.getElementById('bookmarkSession')?.addEventListener('click', () => {
            const sessionId = document.getElementById('sessionModal')?.dataset.currentSession;
            if (sessionId) this.toggleBookmark(sessionId);
        });
        
        document.getElementById('shareSession')?.addEventListener('click', () => {
            const sessionId = document.getElementById('sessionModal')?.dataset.currentSession;
            if (sessionId) this.shareSession(sessionId);
        });
    }
    
    switchView(viewName) {
        this.currentView = viewName;
        
        // Update navigation active state
        document.querySelectorAll('[data-tab]').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab=\"${viewName}\"]`)?.classList.add('active');
        
        // Render appropriate view
        switch (viewName) {
            case 'sessions':
                this.renderSessions();
                break;
            case 'bookmarks':
                this.renderBookmarks();
                break;
            case 'schedule':
                this.renderSchedule();
                break;
            case 'insights':
                this.renderInsights();
                break;
        }
    }
    
    applyFilters() {
        this.filteredSessions = this.sessions.filter(session => {
            // Search filter
            if (this.filterState.search) {
                const searchTerm = this.filterState.search.toLowerCase();
                const searchableText = `${session.title} ${session.session_type} ${session.tags?.join(' ')}`.toLowerCase();
                if (!searchableText.includes(searchTerm)) return false;
            }
            
            // Date filter
            if (this.filterState.date && session.date !== this.filterState.date) {
                return false;
            }
            
            // Priority filter
            if (this.filterState.priority) {
                const priority = this.calculatePriority(session);
                if (priority !== this.filterState.priority) return false;
            }
            
            // Tag filters
            if (this.filterState.tags.size > 0) {
                const sessionTags = new Set(session.tags || []);
                const hasMatchingTag = Array.from(this.filterState.tags).some(tag => 
                    sessionTags.has(tag)
                );
                if (!hasMatchingTag) return false;
            }
            
            return true;
        });
        
        this.renderSessions();
        this.updateStats();
    }
    
    calculatePriority(session) {
        let score = 0;
        
        // Session type scoring
        const sessionType = (session.session_type || '').toLowerCase();
        if (sessionType.includes('workshop')) score += 3;
        else if (sessionType.includes('symposium')) score += 2;
        else if (sessionType.includes('session')) score += 1;
        
        // Tag scoring
        const tags = (session.tags || []).map(tag => tag.toLowerCase());
        const highValueTags = ['adult id', 'pediatric id', 'antimicrobial', 'stewardship', 'ai', 'diagnostic'];
        highValueTags.forEach(tag => {
            if (tags.some(sessionTag => sessionTag.includes(tag))) score += 1;
        });
        
        // View count scoring
        const views = session.views || 0;
        if (views > 500) score += 2;
        else if (views > 300) score += 1;
        
        // CME credits
        if (session.cme_credits) score += 1;
        
        if (score >= 7) return 'High';
        if (score >= 4) return 'Medium';
        return 'Low';
    }
    
    renderSessions() {
        const container = document.getElementById('sessionsContainer');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const noResultsMessage = document.getElementById('noResultsMessage');
        
        if (!container) return;
        
        // Show loading
        loadingIndicator?.classList.remove('d-none');
        noResultsMessage?.classList.add('d-none');
        
        // Clear container
        container.innerHTML = '';
        
        setTimeout(() => {
            if (this.filteredSessions.length === 0) {
                loadingIndicator?.classList.add('d-none');
                noResultsMessage?.classList.remove('d-none');
                return;
            }
            
            const sessionsHTML = this.filteredSessions.map(session => this.createSessionCard(session)).join('');
            container.innerHTML = sessionsHTML;
            
            loadingIndicator?.classList.add('d-none');
        }, 100); // Small delay for smooth UX
    }
    
    createSessionCard(session) {
        const priority = this.calculatePriority(session);
        const isBookmarked = this.bookmarkedSessions.has(session.session_id);
        const tagsHTML = (session.tags || []).slice(0, 4).map(tag => 
            `<span class=\"tag\">${this.escapeHtml(tag)}</span>`
        ).join('');
        
        return `
            <div class="card session-card" data-session-id="${session.session_id}">
                <div class="priority-indicator priority-${priority.toLowerCase()}"></div>
                <div class="card-header">
                    <h6 class="card-title mb-0 text-truncate-2">${this.escapeHtml(session.title || 'Untitled Session')}</h6>
                </div>
                <div class="card-body">
                    <div class="session-meta">
                        <div class="meta-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span>${this.escapeHtml(session.date || 'TBD')}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock"></i>
                            <span>${this.escapeHtml(session.start_time || '')} - ${this.escapeHtml(session.end_time || '')}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${this.escapeHtml(session.location || 'Location TBD')}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-eye"></i>
                            <span>${this.formatNumber(session.views || 0)} views</span>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-secondary">${this.escapeHtml(session.session_type || 'Session')}</span>
                        <span class="badge priority-badge-${priority.toLowerCase()}">${priority} Priority</span>
                    </div>
                    
                    ${session.cme_credits ? `
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-award"></i> ${this.escapeHtml(session.cme_credits)}
                            </small>
                        </div>
                    ` : ''}
                    
                    <div class="session-tags">
                        ${tagsHTML}
                    </div>
                    
                    <div class="session-actions">
                        <button class="btn btn-sm btn-outline-primary bookmark-btn ${isBookmarked ? 'bookmarked' : ''}" 
                                data-session-id="${session.session_id}">
                            <i class="fas fa-bookmark"></i>
                            ${isBookmarked ? 'Bookmarked' : 'Bookmark'}
                        </button>
                        <button class="btn btn-sm btn-primary ms-2" data-session-id="${session.session_id}">
                            <i class="fas fa-info-circle"></i>
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderBookmarks() {
        const bookmarkedSessions = this.sessions.filter(session => 
            this.bookmarkedSessions.has(session.session_id)
        );
        
        const container = document.getElementById('sessionsContainer');
        if (!container) return;
        
        if (bookmarkedSessions.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-bookmark fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No bookmarks yet</h5>
                    <p class="text-muted">Bookmark sessions to access them quickly here.</p>
                </div>
            `;
            return;
        }
        
        const bookmarksHTML = bookmarkedSessions.map(session => this.createSessionCard(session)).join('');
        container.innerHTML = bookmarksHTML;
    }
    
    renderSchedule() {
        const sessionsByDate = this.groupSessionsByDate();
        const container = document.getElementById('sessionsContainer');
        
        if (!container) return;
        
        let scheduleHTML = '';
        Object.keys(sessionsByDate).sort().forEach(date => {
            const sessions = sessionsByDate[date].sort((a, b) => {
                return (a.start_time || '').localeCompare(b.start_time || '');
            });
            
            scheduleHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-gradient-primary text-white">
                        <h5 class="mb-0">${this.escapeHtml(date)} (${sessions.length} sessions)</h5>
                    </div>
                    <div class="card-body p-0">
                        ${sessions.map(session => `
                            <div class="d-flex align-items-center p-3 border-bottom session-schedule-item cursor-pointer" 
                                 data-session-id="${session.session_id}">
                                <div class="me-3">
                                    <div class="fw-bold">${this.escapeHtml(session.start_time || 'TBD')}</div>
                                    <small class="text-muted">${this.escapeHtml(session.end_time || '')}</small>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="fw-bold text-truncate">${this.escapeHtml(session.title || 'Untitled')}</div>
                                    <small class="text-muted">
                                        <i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(session.location || 'Location TBD')}
                                    </small>
                                </div>
                                <div class="text-end">
                                    <span class="priority-indicator priority-${this.calculatePriority(session).toLowerCase()}"></span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = scheduleHTML;
    }
    
    renderInsights() {
        const analytics = this.generateAnalytics();
        const container = document.getElementById('sessionsContainer');
        
        if (!container) return;
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Session Distribution</h6>
                        </div>
                        <div class="card-body">
                            ${Object.entries(analytics.sessionTypes).map(([type, count]) => `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span>${this.escapeHtml(type)}</span>
                                    <span class="badge bg-primary">${count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Top Tags</h6>
                        </div>
                        <div class="card-body">
                            ${analytics.topTags.slice(0, 8).map(([tag, count]) => `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span>${this.escapeHtml(tag)}</span>
                                    <span class="badge bg-info">${count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="col-12 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">MSL Priority Breakdown</h6>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="stat-number text-danger">${analytics.priorityCount.High}</div>
                                    <div class="stat-label">High Priority</div>
                                </div>
                                <div class="col-4">
                                    <div class="stat-number text-warning">${analytics.priorityCount.Medium}</div>
                                    <div class="stat-label">Medium Priority</div>
                                </div>
                                <div class="col-4">
                                    <div class="stat-number text-success">${analytics.priorityCount.Low}</div>
                                    <div class="stat-label">Low Priority</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    showSessionDetails(sessionId) {
        const session = this.sessions.find(s => s.session_id === sessionId);
        if (!session) return;
        
        const modal = document.getElementById('sessionModal');
        const modalTitle = document.getElementById('sessionModalTitle');
        const modalBody = document.getElementById('sessionModalBody');
        
        if (!modal || !modalTitle || !modalBody) return;
        
        modal.dataset.currentSession = sessionId;
        modalTitle.textContent = session.title || 'Session Details';
        
        const priority = this.calculatePriority(session);
        const isBookmarked = this.bookmarkedSessions.has(sessionId);
        
        modalBody.innerHTML = `
            <div class="session-detail-content">
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="text-primary">${this.escapeHtml(session.session_type || 'Session')}</h6>
                        <span class="badge priority-badge-${priority.toLowerCase()}">${priority} Priority</span>
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Date:</strong><br>
                        <span class="text-muted">${this.escapeHtml(session.date || 'TBD')}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Time:</strong><br>
                        <span class="text-muted">${this.escapeHtml(session.start_time || '')} - ${this.escapeHtml(session.end_time || '')}</span>
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Location:</strong><br>
                        <span class="text-muted">${this.escapeHtml(session.location || 'Location TBD')}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Views:</strong><br>
                        <span class="text-muted">${this.formatNumber(session.views || 0)}</span>
                    </div>
                </div>
                
                ${session.cme_credits ? `
                    <div class="mb-3">
                        <strong>CME Credits:</strong><br>
                        <span class="text-muted">${this.escapeHtml(session.cme_credits)}</span>
                    </div>
                ` : ''}
                
                ${session.tags && session.tags.length > 0 ? `
                    <div class="mb-3">
                        <strong>Tags:</strong><br>
                        <div class="mt-2">
                            ${session.tags.map(tag => `<span class="tag me-1 mb-1">${this.escapeHtml(tag)}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${session.moderators && session.moderators.length > 0 ? `
                    <div class="mb-3">
                        <strong>Moderators:</strong><br>
                        ${session.moderators.map(mod => `
                            <div class="mt-2">
                                <div class="fw-semibold">${this.escapeHtml(mod.name || 'Unknown')}</div>
                                ${mod.affiliation ? `<small class="text-muted">${this.escapeHtml(mod.affiliation)}</small>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${session.learning_objectives && session.learning_objectives.length > 0 ? `
                    <div class="mb-3">
                        <strong>Learning Objectives:</strong>
                        <ul class="mt-2">
                            ${session.learning_objectives.map(obj => `<li>${this.escapeHtml(obj)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="mt-4 pt-3 border-top">
                    <small class="text-muted">
                        <i class="fas fa-link"></i>
                        <a href="${this.escapeHtml(session.url || '#')}" target="_blank" class="text-decoration-none">
                            View on EventScribe
                        </a>
                    </small>
                </div>
            </div>
        `;
        
        // Update bookmark button
        const bookmarkBtn = document.getElementById('bookmarkSession');
        if (bookmarkBtn) {
            bookmarkBtn.innerHTML = `<i class="fas fa-bookmark"></i> ${isBookmarked ? 'Remove Bookmark' : 'Bookmark'}`;
            bookmarkBtn.className = `btn ${isBookmarked ? 'btn-warning' : 'btn-outline-warning'}`;
        }
        
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
    
    toggleBookmark(sessionId) {
        if (this.bookmarkedSessions.has(sessionId)) {
            this.bookmarkedSessions.delete(sessionId);
        } else {
            this.bookmarkedSessions.add(sessionId);
        }
        
        // Update local storage
        this.saveUserPreferences();
        
        // Update UI
        this.updateBookmarkButtons(sessionId);
        this.updateStats();
        
        // If currently viewing bookmarks, re-render
        if (this.currentView === 'bookmarks') {
            this.renderBookmarks();
        }
    }
    
    updateBookmarkButtons(sessionId) {
        const isBookmarked = this.bookmarkedSessions.has(sessionId);
        const buttons = document.querySelectorAll(`[data-session-id="${sessionId}"] .bookmark-btn`);
        
        buttons.forEach(btn => {
            btn.innerHTML = `<i class="fas fa-bookmark"></i> ${isBookmarked ? 'Bookmarked' : 'Bookmark'}`;
            btn.className = `btn btn-sm btn-outline-primary bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`;
        });
        
        // Update modal bookmark button if session is currently open
        const modal = document.getElementById('sessionModal');
        if (modal?.dataset.currentSession === sessionId) {
            const modalBookmarkBtn = document.getElementById('bookmarkSession');
            if (modalBookmarkBtn) {
                modalBookmarkBtn.innerHTML = `<i class="fas fa-bookmark"></i> ${isBookmarked ? 'Remove Bookmark' : 'Bookmark'}`;
                modalBookmarkBtn.className = `btn ${isBookmarked ? 'btn-warning' : 'btn-outline-warning'}`;
            }
        }
    }
    
    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return (text || '').toString().replace(/[&<>"']/g, m => map[m]);
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    groupSessionsByDate() {
        const groups = {};
        this.sessions.forEach(session => {
            const date = session.date || 'Unknown Date';
            if (!groups[date]) groups[date] = [];
            groups[date].push(session);
        });
        return groups;
    }
    
    generateAnalytics() {
        const sessionTypes = {};
        const tagCounts = {};
        const priorityCount = { High: 0, Medium: 0, Low: 0 };
        
        this.sessions.forEach(session => {
            // Session types
            const type = session.session_type || 'Unknown';
            sessionTypes[type] = (sessionTypes[type] || 0) + 1;
            
            // Tags
            (session.tags || []).forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
            
            // Priority
            const priority = this.calculatePriority(session);
            priorityCount[priority]++;
        });
        
        const topTags = Object.entries(tagCounts)
            .sort(([,a], [,b]) => b - a);
        
        return {
            sessionTypes,
            topTags,
            priorityCount,
            totalSessions: this.sessions.length,
            totalViews: this.sessions.reduce((sum, s) => sum + (s.views || 0), 0)
        };
    }
    
    updateStats() {
        const totalSessions = document.getElementById('totalSessions');
        const bookmarkedSessions = document.getElementById('bookmarkedSessions');
        const totalViews = document.getElementById('totalViews');
        const highPriority = document.getElementById('highPriority');
        
        if (totalSessions) totalSessions.textContent = this.filteredSessions.length;
        if (bookmarkedSessions) bookmarkedSessions.textContent = this.bookmarkedSessions.size;
        if (totalViews) {
            const views = this.filteredSessions.reduce((sum, s) => sum + (s.views || 0), 0);
            totalViews.textContent = this.formatNumber(views);
        }
        if (highPriority) {
            const highPriorityCount = this.filteredSessions.filter(s => this.calculatePriority(s) === 'High').length;
            highPriority.textContent = highPriorityCount;
        }
    }
    
    populateTagFilters() {
        const tagCounts = {};
        this.sessions.forEach(session => {
            (session.tags || []).forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });
        
        const topTags = Object.entries(tagCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 8);
        
        const container = document.getElementById('tagFilters');
        if (!container) return;
        
        container.innerHTML = topTags.map(([tag, count]) => `
            <button class="btn btn-sm btn-outline-secondary tag-filter" data-tag="${this.escapeHtml(tag)}">
                ${this.escapeHtml(tag)} (${count})
            </button>
        `).join('');
        
        // Add event listeners to tag filters
        container.addEventListener('click', (e) => {
            if (e.target.classList.contains('tag-filter')) {
                const tag = e.target.dataset.tag;
                if (this.filterState.tags.has(tag)) {
                    this.filterState.tags.delete(tag);
                    e.target.classList.remove('active');
                } else {
                    this.filterState.tags.add(tag);
                    e.target.classList.add('active');
                }
                this.applyFilters();
            }
        });
    }
    
    updateConnectionStatus() {
        const statusElement = document.getElementById('connectionStatus');
        const offlineBanner = document.getElementById('offlineBanner');
        
        if (navigator.onLine) {
            statusElement?.innerHTML = '<i class="fas fa-wifi"></i> Online';
            statusElement?.className = 'badge bg-success';
            offlineBanner?.classList.add('d-none');
        } else {
            statusElement?.innerHTML = '<i class="fas fa-wifi-slash"></i> Offline';
            statusElement?.className = 'badge bg-warning';
            offlineBanner?.classList.remove('d-none');
        }
    }
    
    loadUserPreferences() {
        try {
            const bookmarks = localStorage.getItem('idweek2025_bookmarks');
            if (bookmarks) {
                this.bookmarkedSessions = new Set(JSON.parse(bookmarks));
            }
        } catch (error) {
            console.warn('⚠️ Error loading user preferences:', error);
        }
    }
    
    saveUserPreferences() {
        try {
            localStorage.setItem('idweek2025_bookmarks', JSON.stringify([...this.bookmarkedSessions]));
        } catch (error) {
            console.warn('⚠️ Error saving user preferences:', error);
        }
    }
    
    // Additional methods for FAB functionality
    async exportData() {
        try {
            const data = {
                sessions: this.filteredSessions,
                bookmarks: [...this.bookmarkedSessions],
                exportedAt: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `idweek2025-export-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('❌ Export error:', error);
            this.showErrorMessage('Failed to export data');
        }
    }
    
    async syncData() {
        if (!navigator.onLine) {
            this.showErrorMessage('Cannot sync while offline');
            return;
        }
        
        try {
            await this.loadSessionData();
            this.showSuccessMessage('Data synchronized successfully');
        } catch (error) {
            console.error('❌ Sync error:', error);
            this.showErrorMessage('Failed to sync data');
        }
    }
    
    async shareApp() {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'IDWeek 2025 Conference Companion',
                    text: 'Check out the MSL companion app for IDWeek 2025',
                    url: window.location.href
                });
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.warn('⚠️ Share error:', error);
                }
            }
        } else {
            // Fallback: copy to clipboard
            try {
                await navigator.clipboard.writeText(window.location.href);
                this.showSuccessMessage('Link copied to clipboard');
            } catch (error) {
                console.warn('⚠️ Clipboard error:', error);
                this.showErrorMessage('Could not share app');
            }
        }
    }
    
    shareSession(sessionId) {
        const session = this.sessions.find(s => s.session_id === sessionId);
        if (!session) return;
        
        const shareData = {
            title: session.title || 'IDWeek 2025 Session',
            text: `Check out this session from IDWeek 2025: ${session.title}`,
            url: session.url || window.location.href
        };
        
        if (navigator.share) {
            navigator.share(shareData).catch(error => {
                if (error.name !== 'AbortError') {
                    console.warn('⚠️ Share error:', error);
                }
            });
        } else {
            // Fallback: copy session URL
            navigator.clipboard.writeText(session.url || window.location.href).then(() => {
                this.showSuccessMessage('Session link copied to clipboard');
            }).catch(error => {
                console.warn('⚠️ Clipboard error:', error);
            });
        }
    }
    
    showSuccessMessage(message) {
        // You can implement a toast notification system here
        console.log('✅', message);
    }
    
    showErrorMessage(message) {
        // You can implement a toast notification system here
        console.error('❌', message);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.idweekApp = new IDWeekApp();
});