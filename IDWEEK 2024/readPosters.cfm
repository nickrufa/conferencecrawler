<cffile action="read" file="/Users/nickrufa/Development/www/CMEU_sites/occpoc/IDWEEK/poster_output.json" variable="poster_output">
<cfset data = deserializeJSON(poster_output)>

<table border="1">
    <tr>
        <th>Poster ID</th>
        <th>Presenting Authors</th>
    </tr>
    <cfloop array="#data#" index="poster">
        <cfif isdefined("poster.poster_id")><tr>
            <td><cfoutput>#poster.poster_id#</cfoutput></td>
            <td>
                <cfif isdefined("poster.presenting_authors") and arrayLen(poster.presenting_authors) GT 0>
                    <cfloop array="#poster.presenting_authors#" index="author">
                        <cfoutput><strong>#author.name#</strong><br>
                        #author.title#<br>
                        <cfif len(author.affiliation)>#author.affiliation#<br></cfif>
                        <br></cfoutput>
                    </cfloop>
                <cfelse>
                    No presenting authors listed
                </cfif>
            </td>
        </tr></cfif>
    </cfloop>
</table>
<cfsetting showdebugoutput="no">