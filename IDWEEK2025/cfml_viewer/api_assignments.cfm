<cfprocessingdirective pageEncoding="UTF-8">
<cfheader name="Access-Control-Allow-Origin" value="*">
<cfheader name="Access-Control-Allow-Credentials" value="true">
<cfheader name="Access-Control-Allow-Methods" value="GET, POST, OPTIONS">
<cfheader name="Access-Control-Allow-Headers" value="Content-Type">
<cfheader name="Content-Type" value="application/json">

<cfparam name="url.conference_id" default="">
<cfparam name="url.confid" default="">

<cfif structKeyExists(url, "confid") AND len(trim(url.confid))>
    <cfset conference_id = trim(url.confid)>
<cfelseif structKeyExists(url, "conference_id") AND len(trim(url.conference_id))>
    <cfset conference_id = trim(url.conference_id)>
<cfelse>
    <cfoutput>{"error": "confid or conference_id parameter is required"}</cfoutput>
    <cfabort>
</cfif>

<cftry>
    <cfif cgi.request_method EQ "OPTIONS">
        <!--- Handle CORS preflight --->
        <cfabort>

    <cfelseif cgi.request_method EQ "GET">
        <!--- Get assignments --->
        <cfquery name="getAssignments" datasource="conference_crawler">
            SELECT session_id, user_id, assigned_date
            FROM conference_assignments
            WHERE conference_id = <cfqueryparam value="#conference_id#" cfsqltype="cf_sql_integer">
            ORDER BY session_id, user_id
        </cfquery>

        <!--- Debug: Show record count --->
        <!--- <cfoutput><!-- Found #getAssignments.recordCount# assignments for conference #conference_id# --></cfoutput> --->

        <cfset assignments = {}>
        <cfloop query="getAssignments">
            <cfset sessionId = getAssignments.session_id>
            <cfset userId = getAssignments.user_id>
            <cfif NOT structKeyExists(assignments, sessionId)>
                <cfset assignments[sessionId] = []>
            </cfif>
            <cfset arrayAppend(assignments[sessionId], userId)>
        </cfloop>

        <cfoutput>{"assignments": #serializeJSON(assignments)#}</cfoutput>

    <cfelseif cgi.request_method EQ "POST">
        <!--- Save assignments --->
        <cfset requestBody = getHttpRequestData().content>
        <cfset data = deserializeJSON(requestBody)>

        <cfif NOT structKeyExists(data, "assignments")>
            <cfoutput>{"error": "Bad Request", "message": "No assignments data provided"}</cfoutput>
            <cfabort>
        </cfif>

        <cftransaction>
            <!--- Clear existing assignments --->
            <cfquery datasource="conference_crawler">
                DELETE FROM conference_assignments
                WHERE conference_id = <cfqueryparam value="#conference_id#" cfsqltype="cf_sql_integer">
            </cfquery>

            <!--- Insert new assignments --->
            <cfloop array="#data.assignments#" index="assignment">
                <!--- Validate user exists --->
                <cfquery name="userCheck" datasource="conference_crawler">
                    SELECT id FROM conference_users
                    WHERE conference_id = <cfqueryparam value="#conference_id#" cfsqltype="cf_sql_integer">
                      AND id = <cfqueryparam value="#assignment.user_id#" cfsqltype="cf_sql_varchar">
                      AND active = 1
                </cfquery>

                <cfif userCheck.recordCount GT 0>
                    <cfquery datasource="conference_crawler">
                        INSERT INTO conference_assignments (
                            conference_id, session_id, user_id, assigned_date, assigned_by
                        ) VALUES (
                            <cfqueryparam value="#conference_id#" cfsqltype="cf_sql_integer">,
                            <cfqueryparam value="#assignment.session_id#" cfsqltype="cf_sql_varchar">,
                            <cfqueryparam value="#assignment.user_id#" cfsqltype="cf_sql_varchar">,
                            <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">,
                            <cfqueryparam value="system" cfsqltype="cf_sql_varchar">
                        )
                    </cfquery>
                </cfif>
            </cfloop>
        </cftransaction>

        <cfoutput>{"success": true, "message": "Assignments saved successfully", "count": #arrayLen(data.assignments)#}</cfoutput>

    </cfif>

<cfcatch type="any">
    <cfoutput>{"error": "Server error", "message": "#cfcatch.message#"}</cfoutput>
</cfcatch>
</cftry>
<cfsetting showdebugoutput="no">