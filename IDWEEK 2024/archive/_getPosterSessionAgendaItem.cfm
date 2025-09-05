<cfparam name="poster_id" default="695397">
<cfparam name="siteURL" default="https://idweek2024.eventscribe.net/ajaxcalls/PosterInfo.asp?PosterID=">
<!--- cfparam name="siteURL" default="https://idweek2024.eventscribe.net/fsPopup.asp?mode=sessionInfo&PresentationID=" --->

<cfsetting showdebugoutput="no">

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(7, 22);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="#application.dsn#">
    SELECT poster_id
    FROM IDWEEK_Posters_2024
    WHERE 0=0
    AND parsedPosterData IS NULL
    LIMIT 1
</cfquery>

<cfset body_data = '#getAll_IDWEEK_Data.poster_id#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfset cookieHeader = "
                ASPSESSIONIDAECCTAQB=NNACDEBCBHEGBKMIIJMLKDOK;
                ASPSESSIONIDSUASCSQD=KFIDKOOAOLAEABACHAJDPJAC; 
                ASPSESSIONIDSUCSBSRC=ODBKMCCAKJPEOPLFCJNAHBJA; 
                ASPSESSIONIDCGCDQAQB=EKNBDNMCNPHIDBHAHILFFGOA; 
                AWSALB=gH35QugVDKXubRLFIu1vD0Gh3JLhDs5f5Clnyrn2iw+CTeH48FYo44j8zXmm4Y94L+5rqN2drcBeOOupcnCPwn54ZPqmq/B5RjjuAdVN6E9cr2wCCd3mJJ1LYmgi; 
                AWSALBCORS=gH35QugVDKXubRLFIu1vD0Gh3JLhDs5f5Clnyrn2iw+CTeH48FYo44j8zXmm4Y94L+5rqN2drcBeOOupcnCPwn54ZPqmq/B5RjjuAdVN6E9cr2wCCd3mJJ1LYmgi; 
                Domain=idweek2024.eventscribe.net; Path=/;
                _cfuvid=CS79szLi0D_Swmog7Zt_OxhDZ7ZXIl0Wk8rIRjJPO2s-1725992135413-0.0.1.1-604800000; Domain=.eventscribe.net; Path=/;">

            <cfhttp result="result" method="GET" charset="utf-8" url="#siteURL##getAll_IDWEEK_Data.poster_id#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=iso-8859-1">
                <cfhttpparam name="Content-Type" type="Cookie" value="#cookieHeader#">
            </cfhttp>

            <cfset cleanSessionData = result.filecontent>

            <cfquery datasource="#application.dsn#">
                UPDATE IDWEEK_Posters_2024
                SET parsedPosterData = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND poster_id = <cfqueryparam cfsqltype="cf_sql_varchar" value="#poster_id#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.meetings.com/IDWEEK/_getPosterSessionAgendaItem.cfm">
            <!--- cfdump var="#cleanSessionData#" label="cleanSessionData" --->
        </cfoutput>
    </cfloop>
<cfelse>
    Done
</cfif>