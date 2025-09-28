component {
 
    this.name = "medtixCrawler_dev092708";  
    this.applicationTimeout = CreateTimeSpan(7, 0, 0, 0); // 7days
    this.sessionManagement = true;
    this.sessionTimeout = CreateTimeSpan(1, 0, 0, 0); // 1 day
    this.dsn = "conference_crawler";
    this.datasource = "conference_crawler";
    this.directory = "/Users/nancyrobasco/workspace/git/conferencecrawler";
    this.showdebug = "0";
    this.cachebuster = rereplace(now(),'\D','','ALL');
    this.cookieName = '__ga_claris';
    this.myAlgorithm = 'AES';
    this.myEncoding = 'HEX';
    this.cacheOn = 1;
    this.domain = 'local.dev.conferencecrawler.com';
    this.domain_name = 'http://local.dev.conferencecrawler.com';
    this.sitename = 'Local MedTix Conference Crawler';
    this.dump = 0;
    this.searchimplicitscopes = 1;
    this.logger_path = "/Users/nancyrobasco/workspace/git/conferencecrawler.com/admin/logs";
    this.processingDirectives.pageEncoding = "utf-8";
    
    this.hasLogin = 0;

    /* this.customTagPaths = [ expandPath('/myAppCustomTags') ];
    this.mappings = {
        "/foo" = expandPath('/com/myCompany/foo')
    }; changed */

    // see also: http://help.adobe.com/en_US/ColdFusion/10.0/CFMLRef/WSc3ff6d0ea77859461172e0811cbec22c24-750b.html https://helpx.adobe.com/coldfusion/cfml-reference/application-cfc-reference/application-variables.html
    // see also: https://helpx.adobe.com/coldfusion/developing-applications/developing-cfml-applications/designing-and-optimizing-a-coldfusion-application.html

    function onApplicationStart() {

        application.cachebuster = this.cachebuster;
        application.cacheOn = this.cacheOn;
        application.cookieName = this.cookieName;
        application.dsn = this.datasource;
        application.datasource = this.datasource;
        application.directory = this.directory;
        application.domain = this.domain;
        application.domain_name = this.domain_name;
        application.dump = this.dump;
        application.searchimplicitscopes = this.searchimplicitscopes;
        application.logger_path = this.logger_path;
        application.myAlgorithm = this.myAlgorithm;
        application.myEncoding = this.myEncoding;
        application.showdebug = this.showdebug;
        application.sitename = this.sitename;
        application.hasLogin = this.hasLogin;
    
        return true;
    }

    /* 
    function onSessionStart() {
        if (isDefined("sessionId")) {
            session.sessionid = sessionId;
        } else {
            session.sessionid = createUUID();
        }
    } 
    */

    // the target page is passed in for reference,
    // but you are not required to include it
    function onRequestStart( string targetPage ) {
        
        // Check if the user agent is a bot, crawler, or spider
        if (refindNoCase("bot|crawl|spider|facebookexternalhit", cgi.http_user_agent)) {
            // If it's a bot, crawler, or spider
            this.clientManagement = "no";
            this.sessionManagement = "no";
            this.setClientCookies = "no";
            this.setDomainCookies = "no";
            this.clientStorage = "Cookie";
            isBot = 1;
        } else {
            // If it's a regular user
            this.clientManagement = "yes";
            this.sessionManagement = "yes";
            this.sessionTimeout = createTimeSpan(0, 0, 20, 0); // 20 minutes
            this.setClientCookies = "yes";
            this.setDomainCookies = "yes";
            this.clientStorage = "Cookie";
            isBot = 0;
        }

        var securePathsList = "login|register|admin";

        // Check if the requested path requires authentication
        var requestedPath = ListLast(cgi.QUERY_STRING, '=');
        
        if (requestedPath == '') {
            requestedPath = gettoken(cgi.SCRIPT_NAME,1,'/');
        }

        session.authorized = 1;
        
        if (application.hasLogin) {
            // Ensure session.sessionid exists for existing sessions
            if (!structKeyExists(session, "sessionid")) {
                session.sessionid = isDefined("sessionId") ? sessionId : createUUID();
            }
        
            if (0 && ListFindNoCase(securePathsList, requestedPath, '|')) {
            // Validate Session Cookie
            if (!structKeyExists(cookie, "__ga_claris") || !isValidSession(cookie["__ga_claris"])) {

                // Save form data to session scope if the page is "register"
                if (requestedPath == "register" && structKeyExists(form, "fieldnames") && len(form.fieldnames)) {
                    session.tempFormData = duplicate(form);
                }

                cflocation(url="/login?error=timeout", addToken="false");
                abort;
            } else {
                session.authorized = 1;
            }
        }
        
            // LOG OUT
            if (isDefined("url.logout") && trim(url.logout) eq 1 || FindNoCase("logout", CGI.QUERY_STRING)) {
            // Loop through all cookies and delete them
            for (var cn in cookie) {
                try {
                    cfcookie(name=cn, value="", expires="now", preserveCase="true");
                    cfcookie(name=cn, value="", domain=".local.dev.conferencecrawler.com", expires="now", preserveCase="false");
                } catch (any e) {
                    writeDump(#e#);
                }
            }
        
            // cfcookie(name="__ga_claris", value="0", domain=".local.dev.conferencecrawler.com", preserveCase="true");

            if (CGI.HTTPS EQ "on") {
                cfcookie(name="__ga_claris", value=0, domain='.local.dev.conferencecrawler.com', expires=7, httponly=true, secure=true, preserveCase = true);
            } else {
                cfcookie(name="__ga_claris", value=0, domain='.local.dev.conferencecrawler.com', expires=7, httponly=true, secure=false, preserveCase = true);
            }

            // Lock and clear the session scope
            lock scope="session" timeout="10" {
                structClear(session);
                session.authorized = 2;
                session.csrfToken = createUUID();
                session.sessionid = isDefined("sessionId") ? sessionId : createUUID();
            }
        
            application.sessionTimeout = CreateTimeSpan(0, 0, 0, 1);
        }
        }


        include "/_global.cfm";

        include "_userDefinedFunctions.cfm";

        include "/_local.cfm";

        if (application.hasLogin) {
            if ( findnocase("email",cgi.query_string) and findnocase("key",cgi.query_string) ) {
                url.page = 'createAccount';
            }
        }

    }

    function onRequest( string targetPage ) {
        try {
            include arguments.targetPage;
        } catch (any e) {
            writeDump(#application#);
            writeDump(#targetPage#);
            writeDump(#e#);
        }

        try {
            if (application.hasLogin) {
                if (isDefined("cookie.encProfile") and len(trim(cookie.encProfile))) {
                        try {
                            decProfile = decrypt(cookie.encProfile, application.myKey, application.myAlgorithm, application.myEncoding);
                            myProfile = deserializeJSON(decProfile);
                
                            for (key in myProfile) {
                                session[key] = myProfile[key];
                            }

                        } catch (any e) {
                            // writeOutput("Error decrypting cookie.encProfile: " & e.message);
                            writeOutput("Error: Session timeout for local.dev.conferencecrawler.com");

                            for (cn in Cookie) {
                                cfcookie(name=cn, value='', expires='now', preserveCase=true);
                                cfcookie(name=cn, value='', domain='.local.dev.conferencecrawler.com', expires='now', preserveCase=false);
                            }
                        
                            // cfcookie(name='__ga_claris', value='0', domain='.local.dev.conferencecrawler.com', preserveCase=true);

                            if (CGI.HTTPS EQ "on") {
                                cfcookie(name="__ga_claris", value=0, domain='.local.dev.conferencecrawler.com', expires=7, httponly=true, secure=true, preserveCase = true);
                            } else {
                                cfcookie(name="__ga_claris", value=0, domain='.local.dev.conferencecrawler.com', expires=7, httponly=true, secure=false, preserveCase = true);
                            }
                                
                            // Lock the session scope to prevent concurrent access issues
                            lock scope="session" timeout="10" {
                                // Clear the session scope completely
                                structClear(session);
                        
                                // Initialize session variables as needed
                                session.authorized = 2;
                                session.csrfToken = createUUID();
                                session.sessionid = isDefined("sessionId") ? sessionId : createUUID();
                            }
                            writeOutput("<a href='/login?error=timout'>Please log in again.</a>");
                            abort;
                        }
                    }
            }  
        } catch (e any) {
            cleanupCookiesAndSession();
            writeOutput("<a href='/'>Please log in again.</a>");
            abort;
        }
        
        // ✅ MANUALLY CALL onRequestEnd()
        /* In ColdFusion, if you define onRequest(), ColdFusion skips all default request lifecycle hooks — including onRequestEnd() — unless you call them explicitly. 
        ⚠️ Why ColdFusion Skips onRequestEnd()
            When you define onRequest(): ColdFusion assumes you are taking full control over the request lifecycle. 
            That means it will not automatically run onRequestEnd(), onRequestStart(), or even process the requested .cfm unless you tell it to.

            So your flow must be:
                onRequestStart()
                → onRequest()
                    → include targetPage
                    → onRequestEnd()
        */

       	// Force a log to verify we're calling it
        writeLog(file="debuglog", text="📝 Calling onRequestEnd() manually");
        onRequestEnd();
        writeLog(file="debuglog", text="📝 Finished onRequestEnd() call");
    }
            
    boolean function isValidSession(required string sessionToken) {
        // Query to validate session token
        var validateSession = queryExecute(
            "SELECT 1 FROM users WHERE session_token = :sessionToken",
            { sessionToken = { value = sessionToken, cfsqltype = "CF_SQL_VARCHAR" } }
        );
    
        return validateSession.recordCount == 1;
    }

    function onRequestEnd() {

        writeLog(file="debuglog", text="🟡 onRequestEnd started");

        // Logger Info
        function createLogEntry() {
            writeLog(file="debuglog", text="🟠 In createLogEntry");
            
            HAS_FORM_DATA = 0;
            UPID = 0;
            if (isdefined("form.fieldnames")) {
                HAS_FORM_DATA = 1;
            } 
            if (isdefined("session.UserProfileID")) {
                UPID = session.UserProfileID;
            } 
            return {
                "user_agent": cgi.user_agent,
                "date_time": dateTimeFormat(now(), "yyyy-mm-dd HH:nn:ss"),
                "remote_ip": cgi.remote_host,
                "template": cgi.script_name,
                "query_string": cgi.query_string,
                "userprofileid": UPID,
                "hasFormData": HAS_FORM_DATA,
                "Form": [],
                "Session": []
            };
        }
                    
        if (!refindNoCase("bot|crawl|spider|facebookexternalhit", cgi.http_user_agent)) {

            // Create new log entry
            try {
                writeLog(file="debuglog", text="🟢 Creating logEntry");
                logEntry = createLogEntry();
            } catch (any e) {
                writeLog(file="debuglog", text="❌ Error in createLogEntry: #e.message#");
            }

            // Handle Form Data
            if (isDefined("form.fieldnames")) {
                formFields = listToArray(form.fieldnames);
                for (field in formFields) {
                    if (refindNoCase("pwd|passw", field)) {
                        logEntry.Form.append({"#field#": "******"});
                    } else {
                        try {
                            logEntry.Form.append({"#field#": evaluate(field)});
                        } catch (any e) {
                            writeToLog(serializeJSON(e), "0", "0", "error");
                        }
                    }
                }
            } else {
                logEntry.Form.append({"formData": 0});
            }
            writeLog(file="debuglog", text="🧾 Form Data: #serializeJSON(logEntry.Form)#");

            // Handle Session Data
            sessionKeys = structKeyArray(session);
            for (key in sessionKeys) {
                if (key != 'encprofile' && key != 'urltoken') {
                    logEntry.Session.append({"Key": key, "Value": session[key]});
                }
            }

            // Prepare log data for writing
            logData = serializeJSON(logEntry);

            // Add a comma at the end if it's not the first entry of the day
            if (FileExists("#application.logger_path#/#year(now())#/log_#dateformat(now(),'yyyy-mm-dd')#.txt")) {
                logData = "," & logData;
            } else {
                // If it's the first entry of the day, start the JSON array
                logData = "[" & logData;
            }

            // Write to log
            try {
                try {
                    writeLog(file="debuglog", text="🔵 About to call writeToLog()");
                    //writeToLog("testing...", "0", "0", "manual");
                } catch (any e) {
                    writeLog(file="debuglog", text="❌ writeToLog failed: #e.message#");
                }

                writeToLog(logData, logEntry.userprofileid, logEntry.hasFormData);

            } catch (any e) {
                try {
                    writeLog(file="debuglog", text="❌ Outer writeToLog failed: #e.message#");
                    writeToLog(serializeJSON(e), "0", "0", "debuglog");
                } catch (any innerE) {
                    writeLog(file="debuglog", text="❌ Final writeToLog catch also failed: #innerE.message#");
                }
            }
        }

        writeLog(file="debuglog", text="🏁 Reached end of onRequestEnd()");
    }

    function onSessionEnd( struct SessionScope, struct ApplicationScope ) {}

    function onApplicationEnd( struct ApplicationScope ) {}

    function onError( any Exception, string EventName ) {
        writeDump(#Exception#);
    }
}