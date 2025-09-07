<cfprocessingdirective pageEncoding="UTF-8"><cfparam name="poster_id" default="695397">
<cfparam name="siteURL" default="https://idweek2025.eventscribe.net/ajaxcalls/PosterInfo.asp?PosterID=">
<!--- cfparam name="siteURL" default="https://idweek2025.eventscribe.net/fsPopup.asp?mode=sessionInfo&PresentationID=" --->
<cfset lownum = 4>
<cfset highnum = 6>

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(lownum, highnum);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="conference_crawler">
    SELECT poster_id
    FROM IDWEEK_Posters_2025
    WHERE 0=0
    AND (
        rawPosterData IS NULL OR 
        rawPosterData LIKE '<!DOCTYPE%')
    ORDER BY id asc
    LIMIT 1
</cfquery>

<cfset body_data = '#getAll_IDWEEK_Data.poster_id#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfhttp result="result" method="GET" charset="utf-8" url="#siteURL##getAll_IDWEEK_Data.poster_id#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=iso-8859-1">
            </cfhttp>

            <cfset cleanSessionData = result.filecontent>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'.*<!-- POPUP -->','','ALL')>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'<!-- FOOTER -->.*','','ALL')>
            <cfset cleanSessionData = trim(cleanSessionData)>

            <cfquery datasource="conference_crawler">
                UPDATE IDWEEK_Posters_2025
                SET rawPosterData = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND poster_id = <cfqueryparam cfsqltype="cf_sql_varchar" value="#poster_id#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <div style="font-size: 10px;">#htmleditformat(cleanSessionData)#</div><hr>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.conferencecrawler.com/IDWEEK2025/_getPosterSessionAgendaItem.cfm">
            <!--- cfdump var="#cleanSessionData#" label="cleanSessionData" --->
        </cfoutput>
    </cfloop>
    <cfquery name="sessionData" datasource="conference_crawler">
        SELECT count(1) as remaining FROM conference_crawler.IDWEEK_Posters_2025 WHERE 0=0     AND (
        rawPosterData IS NULL OR 
        rawPosterData LIKE '<!DOCTYPE%')
    </cfquery>
    <cfset minutesFromNow = dateAdd("s",(sessionData.remaining*(lownum+highnum)/2),now())>
    <cfoutput>
        #sessionData.remaining#<br>
        #minutesFromNow#<br>
    </cfoutput>
    <cfset decimalHour = sessionData.remaining*((lownum+highnum)/2)/60/60/2>
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