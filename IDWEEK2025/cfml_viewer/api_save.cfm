<cfparam name="url.conference_id" default="1">
<cfsetting showdebugoutput="no">

<cfheader name="Content-Type" value="application/json">

<!--- Handle POST data ---!>
<cfif structKeyExists(form, "assignments")>
    <cfset assignmentsData = form.assignments>
<cfelseif getHttpRequestData().content NEQ "">
    <cfset requestData = deserializeJSON(getHttpRequestData().content)>
    <cfset assignmentsData = requestData.assignments>
<cfelse>
    <cfset assignmentsData = "">
</cfif>

<cftry>
    <!--- Database connection settings - adjust these for your environment ---!>
    <cfset dsn = "your_datasource_name">

    <cfif assignmentsData NEQ "">
        <!--- Parse assignments data ---!>
        <cfif isJSON(assignmentsData)>
            <cfset assignments = deserializeJSON(assignmentsData)>
        <cfelse>
            <cfset assignments = assignmentsData>
        </cfif>

        <!--- Clear existing assignments for this conference ---!>
        <cfquery name="qClearAssignments" datasource="#dsn#">
            DELETE FROM conference_assignments
            WHERE conference_id = <cfqueryparam value="#url.conference_id#" cfsqltype="cf_sql_integer">
        </cfquery>

        <!--- Insert new assignments ---!>
        <cfset insertCount = 0>
        <cfloop collection="#assignments#" item="sessionId">
            <cfset userIds = assignments[sessionId]>
            <cfloop array="#userIds#" index="userId">
                <cfquery name="qInsertAssignment" datasource="#dsn#">
                    INSERT INTO conference_assignments (
                        conference_id,
                        session_id,
                        user_id,
                        assigned_date,
                        created_date
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

        <!--- Success response ---!>
        <cfset response = {
            "success" = true,
            "message" = "Assignments saved successfully",
            "assignmentCount" = insertCount,
            "conferenceId" = url.conference_id
        }>

    <cfelse>
        <!--- No data provided ---!>
        <cfset response = {
            "success" = false,
            "error" = "No assignment data provided"
        }>
    </cfif>

    <cfoutput>#serializeJSON(response)#</cfoutput>

<cfcatch type="any">
    <!--- Error response ---!>
    <cfset errorResponse = {
        "success" = false,
        "error" = cfcatch.message,
        "detail" = cfcatch.detail,
        "type" = cfcatch.type
    }>
    <cfoutput>#serializeJSON(errorResponse)#</cfoutput>
</cfcatch>
</cftry>