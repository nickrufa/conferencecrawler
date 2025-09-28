<cfparam name="url.conference_id" default="1">
<cfsetting showdebugoutput="no">

<cfheader name="Content-Type" value="application/json">

<cftry>
    <!--- Database connection settings - UPDATE THIS with your actual datasource name --->
    <cfset dsn = application.dsn>

    <!--- Check if datasource is configured --->
    <cfif dsn EQ "" OR dsn EQ "your_datasource_name">
        <!--- No datasource configured - return error --->
        <cfset response = {
            "success" = false,
            "error" = "Database not configured. Please update the 'dsn' variable in api_sessions.cfm with your ColdFusion datasource name.",
            "fallback" = true
        }>
        <cfoutput>#serializeJSON(response)#</cfoutput>
        <cfabort>
    </cfif>

    <!--- Query to get sessions from database --->
    <cfquery name="qSessions" datasource="#dsn#">
        SELECT
            session_id,
            session_title,
            session_type,
            session_date,
            start_time,
            end_time,
            location,
            track,
            description,
            speakers,
            created_date
        FROM conference_sessions
        WHERE conference_id = <cfqueryparam value="#url.conference_id#" cfsqltype="cf_sql_integer">
        AND active = 1
        ORDER BY session_date, start_time, session_title
    </cfquery>

    <!--- Convert query to JSON array --->
    <cfset sessionArray = []>
    <cfloop query="qSessions">
        <cfset sessionObj = {
            "session_id" = qSessions.session_id,
            "title" = qSessions.session_title,
            "session_info" = {
                "type" = qSessions.session_type,
                "track" = qSessions.track
            },
            "schedule" = {
                "date" = dateFormat(qSessions.session_date, "yyyy-mm-dd"),
                "start_time" = timeFormat(qSessions.start_time, "HH:mm"),
                "end_time" = timeFormat(qSessions.end_time, "HH:mm"),
                "location" = qSessions.location
            },
            "description" = qSessions.description,
            "speakers" = qSessions.speakers,
            "created_date" = dateFormat(qSessions.created_date, "yyyy-mm-dd") & "T" & timeFormat(qSessions.created_date, "HH:mm:ss") & "Z"
        }>
        <cfset arrayAppend(sessionArray, sessionObj)>
    </cfloop>

    <!--- Return JSON response --->
    <cfset response = {
        "success" = true,
        "sessions" = sessionArray,
        "count" = arrayLen(sessionArray)
    }>

    <cfoutput>#serializeJSON(response)#</cfoutput>

<cfcatch type="any">
    <!--- Error response --->
    <cfset errorResponse = {
        "success" = false,
        "error" = cfcatch.message,
        "detail" = cfcatch.detail
    }>
    <cfoutput>#serializeJSON(errorResponse)#</cfoutput>
</cfcatch>
</cftry>