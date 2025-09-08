<cfprocessingdirective pageEncoding="UTF-8"><cfparam name="presenterid" default="1841088">
<cfparam name="siteURL" default="https://idweek2025.eventscribe.net/ajaxcalls/posterPresenterInfo.asp?PresenterID=">
<!--- cfparam name="siteURL" default="https://idweek2024.eventscribe.net/fsPopup.asp?mode=sessionInfo&PresentationID=" --->
<cfset lownum = 4>
<cfset highnum = 6>

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(lownum, highnum);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="conference_crawler">
    SELECT presenterid, id
    FROM IDWEEK_Faculty_2025
    WHERE 0=0
    AND (
        raw_data IS NULL
        OR
        raw_data like '<!DO%'
    )
    AND presenterid < 2103452
    ORDER BY presenterid desc
    LIMIT 1
</cfquery>
<!--- cfdump var="#getAll_IDWEEK_Data#" label="getAll_IDWEEK_Data" --->

<cfset body_data = '#getAll_IDWEEK_Data.presenterid#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfhttp result="sessionResult" method="GET" charset="utf-8" url="#siteURL##getAll_IDWEEK_Data.presenterid#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=utf-8">
            </cfhttp>

            <cfset cleanSessionData = sessionResult.filecontent>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'.*<!--/##popup_header -->','','ALL')>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'<!--/.main-popup-content-->.*','','ALL')>
            <cfset cleanSessionData = trim(cleanSessionData)>

            <cfquery datasource="conference_crawler">
                UPDATE IDWEEK_Faculty_2025
                SET raw_data = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND presenterid = <cfqueryparam cfsqltype="cf_sql_varchar" value="#presenterid#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <div style="font-size: 10px;">#htmleditformat(cleanSessionData)#</div><hr>
            #getAll_IDWEEK_Data.id# / #getAll_IDWEEK_Data.presenterid# / 
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.conferencecrawler.com/IDWEEK2025/cfml_crawler/_getFacultyItem.cfm">
        </cfoutput>
    </cfloop>
    <cfquery name="sessionData" datasource="conference_crawler">
        SELECT count(1) as remaining FROM conference_crawler.IDWEEK_Faculty_2025 WHERE 0=0 AND (
        raw_data IS NULL
        OR
        raw_data like '<!DO%'
    )
    AND presenterid < 2103452
    </cfquery>
    <cfset minutesFromNow = dateAdd("s",(sessionData.remaining*(lownum+highnum)/4),now())>
    <cfoutput>
        #sessionData.remaining#<br>
        #dateformat(minutesFromNow,'yyyy-mm-dd')# #timeformat(minutesFromNow,'h:mm TT')#<br>
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