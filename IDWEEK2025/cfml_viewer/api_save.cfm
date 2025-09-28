<cfparam name="url.conference_id" default="1">
<cfsetting showdebugoutput="no">

<cfheader name="Content-Type" value="application/json">

<!--- Handle POST data --->
<cfif structKeyExists(form, "assignments")>
    <cfset assignmentsData = form.assignments>
<cfelseif getHttpRequestData().content NEQ "">
    <cfset requestData = deserializeJSON(getHttpRequestData().content)>
    <cfset assignmentsData = requestData.assignments>
<cfelse>
    <cfset assignmentsData = "">
</cfif>

<cftry>
    <!--- Database connection settings - UPDATE THIS with your actual datasource name --->
    <cfset dsn = application.dsn>

    <!--- Check if datasource is configured --->
    <cfif dsn EQ "" OR dsn EQ "your_datasource_name">
        <!--- No datasource configured - return error --->
        <cfset response = {
            "success" = false,
            "error" = "Database not configured. Please update the 'dsn' variable in api_save.cfm with your ColdFusion datasource name.",
            "fallback" = true
        }>
        <cfoutput>#serializeJSON(response)#</cfoutput>
        <cfabort>
    </cfif>

    <cfif assignmentsData NEQ "">
        <!--- Parse assignments data - handle double-stringified JSON from JavaScript --->
        <cftry>
            <cfif isJSON(assignmentsData)>
                <cfset assignments = deserializeJSON(assignmentsData)>
            <cfelse>
                <cfset assignments = assignmentsData>
            </cfif>
        <cfcatch type="any">
            <!--- If parsing fails, try to handle it as a string --->
            <cfset assignments = assignmentsData>
        </cfcatch>
        </cftry>

        <!--- Debug: Log the assignments data structure --->
        <cflog file="api_debug" text="Assignments data type: #getMetadata(assignments).getName()#">
        <cflog file="api_debug" text="Assignments data: #serializeJSON(assignments)#">

        <!--- NOTE: Changed to additive assignment instead of clearing all --->
        <!--- Only clear/insert assignments that are actually being changed --->

        <!--- Insert/update assignments (using INSERT IGNORE or REPLACE if supported) --->
        <cfset insertCount = 0>
        <cftry>
            <cfloop collection="#assignments#" item="sessionId">
                <cflog file="api_debug" text="Processing sessionId: #sessionId#">
                <cfset userIds = assignments[sessionId]>
                <cflog file="api_debug" text="UserIds for session #sessionId#: #serializeJSON(userIds)#">
                <cfloop array="#userIds#" index="userId">
                    <cflog file="api_debug" text="Inserting assignment: session=#sessionId#, user=#userId#">
                <cfquery name="qInsertAssignment" datasource="#dsn#">
                    INSERT IGNORE INTO conference_assignments (
                        conference_id,
                        session_id,
                        user_id,
                        assigned_date,
                        created_at
                    ) VALUES (
                        <cfqueryparam value="#url.conference_id#" cfsqltype="cf_sql_integer">,
                        <cfqueryparam value="#sessionId#" cfsqltype="cf_sql_varchar">,
                        <cfqueryparam value="#userId#" cfsqltype="cf_sql_integer">,
                        <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">,
                        <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
                    )
                </cfquery>
                <cfset insertCount = insertCount + 1>
            </cfloop>
        </cfloop>
        <cfcatch type="any">
            <cflog file="api_debug" text="Error in assignment loop: #cfcatch.message# - #cfcatch.detail#">
            <cfset response = {
                "success" = false,
                "error" = "Error processing assignments: " & cfcatch.message,
                "detail" = cfcatch.detail
            }>
            <cfoutput>#serializeJSON(response)#</cfoutput>
            <cfabort>
        </cfcatch>
        </cftry>

        <!--- Success response --->
        <cfset response = {
            "success" = true,
            "message" = "Assignments saved successfully",
            "assignmentCount" = insertCount,
            "conferenceId" = url.conference_id
        }>

    <cfelse>
        <!--- No data provided --->
        <cfset response = {
            "success" = false,
            "error" = "No assignment data provided"
        }>
    </cfif>

    <cfoutput>#serializeJSON(response)#</cfoutput>

<cfcatch type="any">
    <!--- Error response --->
    <cfset errorResponse = {
        "success" = false,
        "error" = cfcatch.message,
        "detail" = cfcatch.detail,
        "type" = cfcatch.type
    }>
    <cfoutput>#serializeJSON(errorResponse)#</cfoutput>
</cfcatch>
</cftry>