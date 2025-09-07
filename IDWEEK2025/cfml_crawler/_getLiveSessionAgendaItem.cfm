<cfprocessingdirective pageEncoding="UTF-8"><cfparam name="sessionId" default="1489978">
<cfparam name="siteURL" default="https://idweek2025.eventscribe.net/ajaxcalls/SessionInfo.asp?PresentationID=">
<!--- cfparam name="siteURL" default="https://idweek2024.eventscribe.net/fsPopup.asp?mode=sessionInfo&PresentationID=" --->
<cfset lownum = 3>
<cfset highnum = 8>

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(lownum, highnum);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="conference_crawler">
    SELECT sessionId
    FROM IDWEEK_2025
    WHERE 0=0
    AND sessionData IS NULL
    ORDER BY rand()
    LIMIT 1
</cfquery>
<!--- cfdump var="#getAll_IDWEEK_Data#" label="getAll_IDWEEK_Data" --->

<cfset body_data = '#getAll_IDWEEK_Data.sessionId#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfhttp result="sessionResult" method="GET" charset="utf-8" url="#siteURL##getAll_IDWEEK_Data.sessionId#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=utf-8">
            </cfhttp>

            <cfset cleanSessionData = sessionResult.filecontent>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'.*<!-- POPUP -->','','ALL')>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'<!-- FOOTER -->.*','','ALL')>
            <cfset cleanSessionData = trim(cleanSessionData)>

            <cfquery datasource="conference_crawler">
                UPDATE IDWEEK_2025
                SET sessionData = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND sessionId = <cfqueryparam cfsqltype="cf_sql_varchar" value="#sessionId#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <div style="font-size: 10px;">#htmleditformat(cleanSessionData)#</div><hr>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.conferencecrawler.com/IDWEEK2025/_getLiveSessionAgendaItem.cfm">
        </cfoutput>
    </cfloop>
    <cfquery name="sessionData" datasource="conference_crawler">
        SELECT count(1) as remaining FROM conference_crawler.IDWEEK_2025 WHERE 0=0 AND sessionData IS NULL;
    </cfquery>
    <cfset minutesFromNow = dateAdd("s",(sessionData.remaining*(lownum+highnum)/2),now())>
    <cfoutput>
        #sessionData.remaining#<br>
        #minutesFromNow#<br>
    </cfoutput>
    <cfset decimalHour = sessionData.remaining*((lownum+highnum)/2)/60/60>
    <cfscript>
        function decimalHourToTime(decimalHour) {
            // Ensure the input is a number
            decimalHour = val(decimalHour);
            
            // Extract hours (integer part)
            var hours = int(decimalHour);
            
            // Calculate the fractional part for minutes and seconds
            var fractionalHour = decimalHour - hours;
            
            // Convert fractional hour to total seconds
            var totalSeconds = fractionalHour * 3600;
            
            // Extract minutes and remaining seconds
            var minutes = int(totalSeconds / 60);
            var seconds = int(totalSeconds % 60);
            
            // Format the time string
            var timeString = hours & "hr " & 
                             (minutes < 10 ? "0" : "") & minutes & "min " & 
                             (seconds < 10 ? "0" : "") & seconds & "sec";
            
            return timeString;
        }
        
        result = decimalHourToTime(decimalHour);
        writeOutput(result);
    </cfscript>
<cfelse>
    Done
</cfif><cfsetting showdebugoutput="no">