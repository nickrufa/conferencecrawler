<cfquery name="getAllIDWEEKSessionData" datasource="#application.dsn#">
    SELECT *
    FROM IDWEEK_2024
    WHERE 0=0
    ORDER BY id 
</cfquery>
<cfif 0><cfdump var="#getAllIDWEEKSessionData#" label="getAllIDWEEKSessionData"></cfif>
<cfloop query="getAllIDWEEKSessionData">
   
    <cfif not len(trim(getAllIDWEEKSessionData.faculty))>
        <cfset cleanSessionData = trim(getAllIDWEEKSessionData.parsedSessionData)>

        <cfoutput>
            #htmleditformat(cleanSessionData)#<hr>
            <!--- cfset facAll = rereplace(cleanSessionData,'^.+session_name:','','all')>facAll: #facAll#<hr>
            <cfset faculty = "">
            <cfloop list="#facAll#" index="f" delimiters="π">
                <cfset f = f & f>
                #rereplace(replace(f,'faculty:','','ALL'),'\d+','','ALL')#
            </cfloop>
            faculty: #faculty#<hr --->
        </cfoutput>

        <!---
        <cfset location = gettoken(cleanSessionData,'6','π')>
        <cfset locationtmpLeft = gettoken(location,'1',':') & ': '>
        <cfset location = replace(location,locationtmpLeft,'','all')>

        <cfset category = gettoken(cleanSessionData,'7','π')>
        <cfset categorytmpLeft = gettoken(category,'1',':') & ': '>
        <cfset category = replace(category,categorytmpLeft,'','all')>
        
        <cfquery datasource="#application.dsn#">
            update IDWEEK_2024
            set 
            faculty = <cfqueryparam cfsqltype="cf_sql_varchar" value="#trim(faculty)#">
            where 0=0
            and id = <cfqueryparam cfsqltype="cf_sql_integer" value="#trim(id)#">
        </cfquery>
    --->
    </cfif>
</cfloop>