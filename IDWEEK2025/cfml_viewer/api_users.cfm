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
            "error" = "Database not configured. Please update the 'dsn' variable in api_users.cfm with your ColdFusion datasource name.",
            "fallback" = true
        }>
        <cfoutput>#serializeJSON(response)#</cfoutput>
        <cfabort>
    </cfif>

    <!--- Query to get users/MSDs from database --->
    <cfquery name="qUsers" datasource="#dsn#">
        SELECT
            user_id as id,
            user_id as userId,
            CONCAT(first_name, ' ', last_name) as name,
            first_name as firstname,
            last_name as lastname,
            email,
            department,
            role,
            created_date as createdAt,
            assigned_date as assignedDate
        FROM conference_users
        WHERE conference_id = <cfqueryparam value="#url.conference_id#" cfsqltype="cf_sql_integer">
        AND active = 1
        ORDER BY last_name, first_name
    </cfquery>

    <!--- Convert query to JSON array --->
    <cfset userArray = []>
    <cfloop query="qUsers">
        <cfset userObj = {
            "id" = qUsers.id,
            "userId" = qUsers.userId,
            "name" = qUsers.name,
            "firstname" = qUsers.firstname,
            "lastname" = qUsers.lastname,
            "email" = qUsers.email,
            "department" = qUsers.department,
            "role" = qUsers.role,
            "createdAt" = dateFormat(qUsers.createdAt, "yyyy-mm-dd") & "T" & timeFormat(qUsers.createdAt, "HH:mm:ss") & "Z",
            "assignedDate" = dateFormat(qUsers.assignedDate, "yyyy-mm-dd") & "T" & timeFormat(qUsers.assignedDate, "HH:mm:ss") & "Z"
        }>
        <cfset arrayAppend(userArray, userObj)>
    </cfloop>

    <!--- Return JSON response --->
    <cfset response = {
        "success" = true,
        "users" = userArray,
        "count" = arrayLen(userArray)
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