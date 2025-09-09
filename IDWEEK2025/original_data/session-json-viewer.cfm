<cffile action="read" file="/Users/nickrufa/Development/www/CMEU_sites/conferencecrawler/IDWEEK2025/original_data/idweek2025_sessions.json" variable="data">
<cfdump var="#deserializeJSON(data)#">