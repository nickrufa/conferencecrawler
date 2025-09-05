<cfset siteURL = 'https://online.eccmid.org/programme-live-1?programType=listing&embed=1&typeHideAllBut=55&page=11&orderBy=1'>
<cfset cookie_data = 'lbwww8~75100e03d11e67fd27b833a14c39d1d4'>
<cfset cachebuster = rereplace(now(),"\D","","ALL")>

<cfhttp result="result" method="GET" charset="iso-8859-1" url="#siteURL#" useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0">
    <cfhttpparam name="Content-Type" type="Header" value="application/x-www-form-urlencoded; charset=iso-8859-1">
    <cfhttpparam name="PHPSESSID" type="cookie" value="#cookie_data#">
</cfhttp>

<cfset cleanSessionData = result.filecontent>
<cffile action="write" output="#cleanSessionData#" file="#rootDirectory#/eccmid-posters-#cachebuster#.html">