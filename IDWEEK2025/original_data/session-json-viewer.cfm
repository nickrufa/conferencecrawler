<cffile action="read" file="/Users/nickrufa/Development/www/CMEU_sites/conferencecrawler/IDWEEK2025/idweek2025_sessions.json" variable="data">

<cfset data = deserializeJSON(data)>
<cfoutput>#arraylen(data)#</cfoutput>
<cfloop index="s" from="1" to="#arraylen(data)#">
    <cfset sesStruct = data[s]>
    <cfset myPres = sesStruct['presentations']>

    <cfset mySessionInfo = sesStruct['session_info']>
    <cfset myFullTitle = mySessionInfo['full_title']>
    <cfset mySessionType = mySessionInfo['type']>

    <cfset mySchedule = sesStruct['schedule']>
    <cfset mySessionDate = mySchedule['date']>
    <cfset mySessionTime = mySchedule['time']>
    <cfset mySessionLocation = mySchedule['location']>

    <!--- cfdump var="#myPres#"><br --->
    <cfloop index="i" from="1" to="#arraylen(myPres)#">
        <hr>s:<cfoutput>#s#</cfoutput><hr>
        <cfset mySpeakers = myPres[i].speakers>
        <cfif isStruct(mySpeakers)>

            <cfset myModerators = mySpeakers['workshop moderator(s)']>
            <cfloop index="p" from="1" to="#arrayLen(myModerators)#">
                <cfset aSpeaker = myModerator[p]>
                MODERATOR STRUCT: <cfdump var="#aSpeaker#">--<br>
            </cfloop>

        <cfelseif isArray(mySpeakers)>
            <cfloop index="p" from="1" to="#myPres[i].speaker_count#">
                <cfset aSpeaker = mySpeakers[p]>
                SPEAKER ARRAY: <cfdump var="#aSpeaker#"><br>
            </cfloop>
        </cfif>

        <cfset myTime = myPres[i].time>
        <cfset myTitle = myPres[i].title>
        <cfoutput>
            #myFullTitle#<br>
            #mySessionType#<br>
            #mySessionDate#<br>
            #mySessionTime#<br>
            #mySessionLocation#<br>
            #myTime#<br>
            #myTitle#
        </cfoutput>
        <hr>
    </cfloop>
</cfloop>