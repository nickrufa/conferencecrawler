<cfprocessingdirective pageEncoding="UTF-8"><cfparam name="sessionId" default="1489978">
<cfparam name="siteURL" default="https://idweek2024.eventscribe.net/ajaxcalls/SessionInfo.asp?PresentationID=">
<!--- cfparam name="siteURL" default="https://idweek2024.eventscribe.net/fsPopup.asp?mode=sessionInfo&PresentationID=" --->
<cfset lownum = 6>
<cfset highnum = 11>

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(lownum, highnum);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="#application.dsn#">
    SELECT sessionId
    FROM IDWEEK_2024
    WHERE 0=0
    AND rawSessionData IS NULL
    LIMIT 1
</cfquery>
<!--- cfdump var="#getAll_IDWEEK_Data#" label="getAll_IDWEEK_Data" --->

<cfset body_data = '#getAll_IDWEEK_Data.sessionId#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfset cookieHeader = "
                ASPSESSIONIDCGBASARD=LFFEPMKDFLPDKECEFHJCNIME;
                AWSALB=xa0LFFyF+CywmtEjd9vzhqb93NmrHjnf2dviHsOHd9n0hkdqs/21LZFG/mSyTk6kNp32/v9FV6G/Z0rUmvHVtU4h35cycEWApIZLVYv3Zt7XmIpuC41I+TWnojQl; 
                AWSALBCORS=xa0LFFyF+CywmtEjd9vzhqb93NmrHjnf2dviHsOHd9n0hkdqs/21LZFG/mSyTk6kNp32/v9FV6G/Z0rUmvHVtU4h35cycEWApIZLVYv3Zt7XmIpuC41I+TWnojQl;  Domain=idweek2024.eventscribe.net; Path=/;
                _cfuvid=G5_stWxOT2igL30Ha1eKw_YPp0sH2jwUDFwBbIP67iI-1726537043881-0.0.1.1-604800000;
                _ga=GA1.1.2143032362.1726511209;
                _ga_553927WRCC=GS1.1.1726537044.2.1.1726537119.0.0.0;
                _gid=GA1.2.390690180.1726511209; Domain=.eventscribe.net; Path=/;">

            <cfhttp result="sessionResult" method="GET" charset="utf-8" url="#siteURL##getAll_IDWEEK_Data.sessionId#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=utf-8">
                <cfhttpparam name="Content-Type" type="Cookie" value="#cookieHeader#">
            </cfhttp>

            <cfset cleanSessionData = sessionResult.filecontent>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'.*<!-- POPUP -->','','ALL')>
            <cfset cleanSessionData = rereplaceNoCase(cleanSessionData,'<!-- FOOTER -->.*','','ALL')>
            <cfset cleanSessionData = trim(cleanSessionData)>

            <cfquery datasource="#application.dsn#">
                UPDATE IDWEEK_2024
                SET rawSessionData = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND sessionId = <cfqueryparam cfsqltype="cf_sql_varchar" value="#sessionId#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <div style="font-size: 10px;">#htmleditformat(cleanSessionData)#</div><hr>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.meetings.com/IDWEEK/cfml_crawler/_getLiveSessionAgendaItem.cfm">
        </cfoutput>
    </cfloop>
    <cfquery name="sessionData" datasource="#application.dsn#">
        SELECT count(1) as remaining FROM conference_crawler.IDWEEK_2024 WHERE 0=0 AND rawSessionData IS NULL;
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