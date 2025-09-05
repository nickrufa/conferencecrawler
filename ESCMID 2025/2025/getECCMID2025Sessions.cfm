<cfquery name="getsessionx" datasource="medinfo">
    select sessionId, sessionData from ECCMID_2025
    where 0=0
    and sessionid NOT LIKE ('MEET%')
    and sessionid NOT LIKE ('S2')
    and sessionid NOT LIKE ('S3')
    and sessionid NOT LIKE ('S4')
    and sessionid NOT LIKE ('SC%')
    and sessionid NOT LIKE ('MOVIE%')
    and sessionid NOT LIKE ('OPEN%')
</cfquery>
<cfloop query="getsessionx">
    <cfset catName = rereplace(sessionData,'.*<div class="modal-title-cat mt-5 mb-2">\s+<h4 class="modal-cat-name programmeCategoryColor\d+">(.+)</h4>\s+</div>\s+<h3>.*','\1','ALL')>
    <cfoutput><h1>#sessionId#</h1><h2>#catName#</h2><hr></cfoutput>
</cfloop>
<cfsetting showdebugoutput="0">
