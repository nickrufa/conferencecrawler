<cfprocessingdirective pageEncoding="UTF-8"><!DOCTYPE html><cffile action="read" file="#ExpandPath('xxoutput.json')#" variable="fileContent">
<!--- cfdump var="#deserializeJSON(fileContent)#" --->
<cffile action="read" file="#ExpandPath('xxoutput.json')#" variable="fileContent">
<cfset sessionData = deserializeJSON(fileContent)>

<table>
    <cfoutput>
        <cfloop array="#sessionData#" index="session">
            <tr>
                <cftry>
                    <td>#session.url#</td>
                    <td>#session.session_type#</td>
                    <td>#session.title#</td>
                    <td>#session.date#</td>
                    <td>#session.time#</td>
                    <td>#session.location#</td>
                    <cfcatch type="any">
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </cfcatch>
                </cftry>
            </tr>
        </cfloop>
    </cfoutput>
</table>
<cfsetting showdebugoutput=0>