<cfsetting showdebugoutput="no">
<cfparam name="url.thisID" default="266">
<cfquery name="getRawData" datasource="occ3">
    select rawSessionData
    from IDWEEK_2024
    where 0=0
    and id = <cfqueryparam cfsqltype="cf_sql_integer" value="#trim(url.thisID)#">
    LIMIT 1
</cfquery>

<cfset cleanSessionData = rereplaceNoCase(getRawData.rawSessionData,'<h2','   <h2','ALL')>

<cfoutput>#htmleditformat(cleanSessionData)#</cfoutput>