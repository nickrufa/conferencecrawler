<cfsetting showdebugoutput="1">
<cfparam name="url.table" default="IDWEEK_Posters_2025">
<cfparam name="url.rawField" default="rawPosterData">
<cfparam name="url.thisID" default="1">

<!--- Debug output to show current parameters --->
<div style="background: #f0f0f0; padding: 10px; margin: 10px 0; border: 1px solid #ccc;">
    <strong>Debug Info:</strong><br>
    Current ID: <cfoutput>#url.thisID#</cfoutput><br>
    Table: <cfoutput>#url.table#</cfoutput><br>
    Raw Field: <cfoutput>#url.rawField#</cfoutput>
</div>
<cfquery name="getAllIDWEEKSessionData" datasource="conference_crawler">
    SELECT id, #url.rawField# as data
    FROM #url.table#
    WHERE 0=0
    ORDER BY id
</cfquery>

<cfoutput query="getAllIDWEEKSessionData">
    <div style="background: ##ffffcc; padding: 5px; margin: 5px 0; border: 2px solid ##ff6600; font-weight: bold; font-size: 16px;">
        🆔 POSTER ID: #getAllIDWEEKSessionData.id# (URL param thisID: #url.thisID#)
    </div>
    #trim(getAllIDWEEKSessionData.data)#
</cfoutput>

<cfquery name="getFilteredIDWEEKSessionData" dbtype="query">
    SELECT *
    FROM getAllIDWEEKSessionData
    WHERE 0=0
    ORDER BY id
</cfquery>

<!--- Debug output for query results --->
<div style="background: #e6f3ff; padding: 10px; margin: 10px 0; border: 1px solid #0066cc;">
    <strong>Query Results:</strong><br>
    Total records from getAllIDWEEKSessionData: <cfoutput>#getAllIDWEEKSessionData.recordCount#</cfoutput><br>
    Total records from getFilteredIDWEEKSessionData: <cfoutput>#getFilteredIDWEEKSessionData.recordCount#</cfoutput>
</div>

<cfif 0><cfdump var="#getFilteredIDWEEKSessionData#" label="getFilteredIDWEEKSessionData"></cfif>

<cfif isnumeric(trim(url.thisID))>
    <cfquery name="getOneIDWEEKSession" dbtype="query">
        SELECT *
        FROM getAllIDWEEKSessionData
        WHERE 0=0
        AND id = <cfqueryparam cfsqltype="cf_sql_integer" value="#url.thisID#">
        ORDER BY id,sessionId, sessionType 
    </cfquery>
    <cfif 0><cfdump var="#getOneIDWEEKSession#" label="getOneIDWEEKSession"></cfif>
</cfif>

<cfquery name="getIDWEEKDates" dbtype="query">
    SELECT distinct(startDate)
    FROM getAllIDWEEKSessionData
</cfquery>
<cfif 0><cfdump var="#getIDWEEKDates#" label="getIDWEEKDates"></cfif>

<cfquery name="getIDWEEKSessionTypes" dbtype="query">
    SELECT distinct(sessionType) as sessionType
    FROM getAllIDWEEKSessionData
    WHERE 0=0
</cfquery>
<cfif 0><cfdump var="#getIDWEEKSessionTypes#" label="getIDWEEKSessionTypes"></cfif>

<cfquery name="getFilteredIDWEEKSessionTypes" dbtype="query">
    SELECT distinct(sessionType) as sessionType
    FROM getFilteredIDWEEKSessionData
    WHERE 0=0
</cfquery>
<cfif 0><cfdump var="#getFilteredIDWEEKSessionTypes#" label="getFilteredIDWEEKSessionTypes"></cfif>

<div class="container">

    <cfoutput>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body bg-light">
                        <div class="text-center my-2">
                            <a class="btn btn-sm btn-outline-secondary<cfif not len(trim(url.thisStartDate))> active</cfif>" href="/index.cfm?page=sessions&amp;thisSessionType=#url.thisSessionType#&amp;url.thisStartDate=">ALL</a>
                            <cfloop query="getIDWEEKDates">
                                <a class="btn btn-sm btn-outline-secondary<cfif getIDWEEKDates.startDate is '#url.thisStartDate#'> active</cfif>" href="/index.cfm?page=sessions&amp;thisSessionType=#url.thisSessionType#&amp;url.thisStartDate=#startDate#">#startDate#</a> 
                            </cfloop>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </cfoutput>

    <cfoutput>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body bg-light">
                        <div class="text-center my-2">
                            <a class="btn btn-sm btn-outline-info<cfif not len(trim(getFilteredIDWEEKSessionTypes.sessionType))> active</cfif>" href="/index.cfm?page=sessions&amp;thisSessionType=&amp;url.thisStartDate=#url.thisStartDate#">ALL</a> 
                            <cfloop query="getFilteredIDWEEKSessionTypes">
                                <a class="btn btn-sm btn-outline-info<cfif getFilteredIDWEEKSessionTypes.sessionType is '#url.thisSessionType#'> active</cfif>" href="/index.cfm?page=sessions&amp;thisSessionType=#getFilteredIDWEEKSessionTypes.sessionType#&amp;url.thisStartDate=#url.thisStartDate#"><cfif len(trim(getFilteredIDWEEKSessionTypes.sessionType))>#getFilteredIDWEEKSessionTypes.sessionType#<cfelse>Other</cfif></a> 
                                <cfif NOT currentrow mod 5></div><div class="text-center my-2"></cfif>
                            </cfloop>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </cfoutput>

    <div class="row">
        <div class="col-12">
            <div class="card bg-primary">
                <div class="card-body bg-light">
                    <div class="text-center my-2">
                        <cfset breakCounter = 1>
                        <cfoutput query="getFilteredIDWEEKSessionData">
                            <cfif sessionType is "#trim(url.thisSessionType)#">
                                <a class="btn btn-sm btn-outline-primary m-2<cfif getFilteredIDWEEKSessionData.id is '#url.thisID#'> active</cfif>" href="/index.cfm?page=sessions&amp;thisID=#id#&amp;thisPageAction=view&amp;thisSessionType=#url.thisSessionType#&amp;url.thisStartDate=#url.thisStartDate#">#sessionId#</a> 
                                <cfif NOT breakCounter mod 10></div><div class="text-center my-2"></cfif>
                                <cfset breakCounter = breakCounter+1>
                            </cfif>
                        </cfoutput>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <cfif isnumeric(trim(url.thisID))>
        <div class="row">
            <div class="col-9">
                <div class="card bg-primary">
                    <div class="card-body bg-light">
                        <cfif 0><cfdump var="#getOneIDWEEKSession#" label="getOneIDWEEKSession"></cfif>

                        <cfset cleanSessionData = EncodeForHTML(trim(getOneIDWEEKSession.sessionData))>
                        <cfset cleanSessionData = CharsetDecode(getOneIDWEEKSession.sessionData, "latin1")>
                        <cfset cleanSessionData = CharsetEncode(cleanSessionData, "latin1")>
                        <cfset cleanSessionData = replace(cleanSessionData,'modal fade','','ALL')>
                        <cfset cleanSessionData = replace(cleanSessionData,'modal-','','ALL')>
                        <cfset cleanSessionData = replace(cleanSessionData,'src','src="" src-url','ALL')>
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                <cfoutput>#cleanSessionData#</cfoutput>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
            <div class="col-3">
                <div class="card bg-primary">
                    <div class="card-body bg-light">
                        <cfif 0><cfdump var="#getOneIDWEEKSession#" label="getOneIDWEEKSession"></cfif>

                        <cfset cleanSessionData = trim(getOneIDWEEKSession.parsedSessionData)>
                        <cfoutput>
                            <cfset location = gettoken(cleanSessionData,'6','π')>
                            <cfset locationtmpLeft = gettoken(location,'1',':') & ': '>
                            <cfset location = replace(location,locationtmpLeft,'','all')>location: #location#<hr>

                            <cfset category = gettoken(cleanSessionData,'7','π')>
                            <cfset categorytmpLeft = gettoken(category,'1',':') & ': '>
                            <cfset category = replace(category,categorytmpLeft,'','all')>category: #category#<hr>

                            <!--- cfset yearmonthday = gettoken(cleanSessionData,'1','π')>
                            <cfset yearmonthday = gettoken(yearmonthday,'2',':')>
                            <cfset yearmonthday = '2024-' & gettoken(yearmonthday,'2','/') & '-' & trim(gettoken(yearmonthday,'1','/'))>

                            <cfset sessionLocalStartEndTime = gettoken(cleanSessionData,'2','π')>
                            <cfset tmpLeft = gettoken(sessionLocalStartEndTime,'1',':') & ':'>
                            <cfset tmpRight = replace(sessionLocalStartEndTime,tmpLeft,'','ALL')>
                            <cfset tmpStartTime = gettoken(tmpRight,'1','-')>
                            <cfset tmpEndTime = gettoken(tmpRight,'2','-')>

                            <cfset sessionLocalStart = yearmonthday & ' ' & tmpStartTime>
                            <cfset sessionLocalEnd = yearmonthday & ' ' & tmpEndTime>

                            <cfset sessionType = gettoken(cleanSessionData,'4','π')>
                            <cfset sessionType = gettoken(sessionType,'2',':') --->

                        </cfoutput>

                        <!--- <cfset cleanSessionData = replace(cleanSessionData,'π','<br>','ALL')> --->
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                <cfoutput>
                                    <!--- cfquery datasource="#application.dsn#">
                                        update IDWEEK_2025
                                        set
                                            sessionLocalStart = <cfqueryparam cfsqltype="cf_sql_timestamp" value="#trim(sessionLocalStart)#">
                                            , sessionLocalEnd = <cfqueryparam cfsqltype="cf_sql_timestamp" value="#trim(sessionLocalEnd)#">
                                            , sessionType = <cfqueryparam cfsqltype="cf_sql_varchar" value="#trim(sessionType)#">
                                        where 0=0
                                        and id = <cfqueryparam cfsqltype="cf_sql_integer" value="#trim(thisID)#">
                                    </cfquery --->
                                    <hr>
                                    #cleanSessionData#
                                </cfoutput>
                            </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </cfif>

</div --->