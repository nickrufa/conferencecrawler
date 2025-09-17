<cfparam name="presenterid" default="1815391">
<cfparam name="rnd" default="0.705548">
<cfparam name="siteURL" default="https://idweek2024.eventscribe.net/ajaxcalls/PresenterInfo.asp?efp=UUVLUVdIQUkyMTg2Mg">

<cfsetting showdebugoutput="no">
<cfset lownum = 7>
<cfset highnum = 16>

<cfscript>
    function CreateRandomSixteenThirtySix() {
        return randRange(lownum, highnum);
    }
</cfscript>

<cfquery name="getAll_IDWEEK_Data" datasource="#application.dsn#">
    SELECT presenterid, rnd
    FROM IDWEEK_Faculty_2024
    WHERE 0=0
    AND raw_data IS NULL
    LIMIT 1
</cfquery>

<cfset body_data = '#getAll_IDWEEK_Data.presenterid#'>

<cfif getAll_IDWEEK_Data.recordcount>
    <cfloop query="getAll_IDWEEK_Data">
        <cftry>

            <cfset cookieHeader = "
                ASPSESSIONIDAECCTAQB=NNACDEBCBHEGBKMIIJMLKDOK;
                ASPSESSIONIDCGCDQAQB=FDJNDNMCDJKKFGJPKHLAIIJF;
                ASPSESSIONIDSUASCSQD=KFIDKOOAOLAEABACHAJDPJAC;
                ASPSESSIONIDSUCSBSRC=ODBKMCCAKJPEOPLFCJNAHBJA;
                AWSALB=JaqrKt0devgzxI3wZNOJ951yY5uhmu/MTSkozKRfUmvk/zJ3pTy70ifVAYP7Go3EBdLvnWeTPHaFSlLKVP12AU7Jceh04iL47bJVwafd38341k/ElG6k50Lbb/Vv;
                AWSALBCORS=JaqrKt0devgzxI3wZNOJ951yY5uhmu/MTSkozKRfUmvk/zJ3pTy70ifVAYP7Go3EBdLvnWeTPHaFSlLKVP12AU7Jceh04iL47bJVwafd38341k/ElG6k50Lbb/Vv;
                Domain=idweek2024.eventscribe.net; Path=/;
                _cfuvid=CS79szLi0D_Swmog7Zt_OxhDZ7ZXIl0Wk8rIRjJPO2s-1725992135413-0.0.1.1-604800000; Domain=.eventscribe.net; Path=/;">

            <cfhttp result="result" method="GET" charset="utf-8" url="#siteURL#&PresenterID=#trim(getAll_IDWEEK_Data.presenterid)#&rnd=#trim(getAll_IDWEEK_Data.rnd)#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36">
                <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=iso-8859-1">
                <cfhttpparam name="Content-Type" type="Cookie" value="#cookieHeader#">
            </cfhttp>

            <cfset cleanSessionData = result.filecontent>

            <cfquery datasource="#application.dsn#">
                UPDATE IDWEEK_Faculty_2024
                SET raw_data = <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#cleanSessionData#">
                WHERE 0=0
                AND presenterid = <cfqueryparam cfsqltype="cf_sql_varchar" value="#presenterid#">
            </cfquery>

            <cfcatch type="any">
                <cfdump var="#cfcatch#" label="error"><cfabort>
            </cfcatch>
        </cftry>
        <cfoutput>
            <meta http-equiv="refresh" content="#CreateRandomSixteenThirtySix()#; url=http://local.dev.meetings.com/IDWEEK/cfml_crawler/_getFacultyItem.cfm">
            <!--- cfdump var="#cleanSessionData#" label="cleanSessionData" --->
        </cfoutput>
    </cfloop>
    <cfquery name="facultyData" datasource="#application.dsn#">
        SELECT count(1) as remaining FROM conference_crawler.IDWEEK_Faculty_2024 WHERE 0=0 AND raw_data IS NULL;
    </cfquery>
    <cfset minutesFromNow = dateAdd("s",(facultyData.remaining*(lownum+highnum)/2),now())>
    <cfoutput>
        #facultyData.remaining#<br>
        #minutesFromNow#<br>
    </cfoutput>
    <cfset decimalHour = facultyData.remaining*((lownum+highnum)/2)/60/60>
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
</cfif>