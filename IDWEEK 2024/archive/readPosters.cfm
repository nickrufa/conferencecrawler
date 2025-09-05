<cffile action="read" file="#expandPath('./extractedPosterData.json')#" variable="mydata">

<cfset data = deserializeJSON(mydata)>

<cfif isArray(data) AND arrayLen(data) GT 0>
    <table>
        <tr>
            <th>Name</th>
            <th>Title</th>
            <th>Affiliation</th>
        </tr>
        <cfloop array="#data#" index="poster">
            <cftry>
                <cfif isArray(poster.presenters) AND arrayLen(poster.presenters) GT 0>
                    <cfset firstPresenter = poster.presenters[1]>
                    <cfoutput>
                    <tr>
                        <td>#firstPresenter.name#</td>
                        <td>#firstPresenter.title#</td>
                        <td>#firstPresenter.affiliation#</td>
                    </tr>
                    </cfoutput>
                </cfif>
                <cfcatch type="any">
                    <tr>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                    </tr>
                 </cfcatch>
            </cftry>
        </cfloop>
    </table>
<cfelse>
    <cfoutput>No data found.</cfoutput>
</cfif>
<cfsetting showdebugoutput="false">