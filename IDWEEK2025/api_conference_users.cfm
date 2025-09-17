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
    </cfif>

    <cfquery name="getUsers" datasource="conference_crawler">
        SELECT
            id as user_id,
            CONCAT(COALESCE(firstname, ''), ' ', COALESCE(lastname, '')) as name,
            COALESCE(firstname, '') as firstname,
            COALESCE(lastname, '') as lastname,
            COALESCE(email, '') as email,
            COALESCE(department, '') as department,
            COALESCE(title, '') as title,
            COALESCE(degree, '') as degree,
            external_id,
            COALESCE(external_system, '') as external_system,
            active,
            created_at
        FROM conference_users
        WHERE conference_id = <cfqueryparam value="#conference_id#" cfsqltype="cf_sql_integer">
          AND active = 1
        ORDER BY lastname, firstname
    </cfquery>

    <cfset result = []>
    <cfloop query="getUsers">
        <cfset userObj = {}>
        <cfset userObj.id = getUsers.user_id>
        <cfset userObj.user_id = getUsers.user_id>
        <cfset userObj.name = getUsers.name>
        <cfset userObj.firstname = getUsers.firstname>
        <cfset userObj.lastname = getUsers.lastname>
        <cfset userObj.email = getUsers.email>
        <cfset userObj.department = getUsers.department>
        <cfset userObj.title = getUsers.title>
        <cfset userObj.degree = getUsers.degree>
        <cfset userObj.external_id = getUsers.external_id>
        <cfset userObj.external_system = getUsers.external_system>
        <cfset userObj.conference_role = "msd">
        <cfset userObj.active = (getUsers.active EQ 1)>
        <cfset userObj.assigned_date = getUsers.created_at>
        <cfset userObj.created_at = getUsers.created_at>
        <cfset arrayAppend(result, userObj)>
    </cfloop>

    <cfoutput>#serializeJSON(result)#</cfoutput>

<cfcatch type="any">
    <cfoutput>{"error": "Database error", "message": "#cfcatch.message#"}</cfoutput>
</cfcatch>
</cftry>
<cfsetting showdebugoutput="no">