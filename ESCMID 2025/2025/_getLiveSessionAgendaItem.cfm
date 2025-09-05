<cfparam name="sessionId" default="3667">
<cfparam name="siteURL" default="https://eccmid2025.key4.live/fo-user-display-session-details.php">

<cfsetting showdebugoutput="no">

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(7, 22);
    }
</cfscript>

<cfquery name="getAllECCMIDData" datasource="medinfo">
    SELECT sessionId
    FROM ECCMID_2025
    WHERE 0=0
    AND (
        sessionData IS NULL
        OR
        dc < '#dateformat(dateAdd("d",-4,now()),"YYYY-MM-DD")#'
    )
    LIMIT 1
</cfquery>

<cfset body_data = 'idCat=1&sessionRef=#getAllECCMIDData.sessionId#&timezone=Europe%2FParis&defaultTimezone=Europe%2FParis&dispCountry=&target=_blank&embed=true&dispCities=&firstnameFull=&page='>
<cfset cookie_data = '9407e3f36370c52980a1d8cc66a3c007'>

<cfif getAllECCMIDData.recordcount>
    <cfloop query="getAllECCMIDData">
        <cftry>
            <cfhttp result="result" method="POST" charset="iso-8859-1" url="#siteURL#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=iso-8859-1">
                <cfhttpparam name="PHPSESSID" type="cookie" value="#cookie_data#">
                <cfhttpparam name="q" type="body" value="#body_data#">
            </cfhttp>

            <cfset cleanSessionData = result.filecontent>

            <cfquery datasource="#application.dsn#">
                UPDATE ECCMID_2025
                SET sessionData = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                , dc = '#dateformat(now(),"YYYY-MM-DD")# #timeformat(now(),"HH:mm:ss")#'
                WHERE 0=0
                AND sessionId = <cfqueryparam cfsqltype="cf_sql_varchar" value="#sessionId#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.meetings.com/_getLiveSessionAgendaItem.cfm">
        </cfoutput>
    </cfloop>
<cfelse>
    Done
</cfif>