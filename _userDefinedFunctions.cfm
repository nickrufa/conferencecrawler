<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="writeToLog" access="public" returntype="string" output="false">
    <cfargument name="logData" type="string" required="true" default="" />
    <cfargument name="UPID" type="string" required="false" default="0" />
    <cfargument name="hasFormData" type="string" required="false" default="0" />
    <cfargument name="logName" type="string" required="false" default="" />

    <cftry>
        <!--- <cfset writeLog(file="debuglog", text="🛠 Inside writeToLog: Starting")> --->

        <cfif NOT DirectoryExists("#application.logger_path#/#year(now())#")>
            <cfdirectory action="create" directory="#application.logger_path#/#year(now())#">
        </cfif>

        <cfif len(trim(arguments.logName))>
            <cfset outfile = "#application.logger_path#/#year(now())#/log_#arguments.logName#_#dateformat(now(),'yyyy-mm-dd')#.txt">
        <cfelse>
            <cfset outfile = "#application.logger_path#/#year(now())#/log_#dateformat(now(),'yyyy-mm-dd')#.txt">
        </cfif>

        <!---  <cfset writeLog(file="debuglog", text="🛠 Log file path: #outfile#")> --->

        <!--- Optional DB logging --->
        <cfquery name="write_activity_log">
            insert into activity_log (
                logData, http_referer, query_string,
                userProfileId, hasFormData, template, logName
            ) values (
                <cfqueryparam cfsqltype="cf_sql_longvarchar" value="#arguments.logData#">,
                <cfqueryparam cfsqltype="cf_sql_varchar" value="#cgi.http_referer#">,
                <cfqueryparam cfsqltype="cf_sql_varchar" value="#cgi.query_string#">,
                <cfqueryparam cfsqltype="cf_sql_varchar" value="#arguments.UPID#">,
                <cfqueryparam cfsqltype="cf_sql_varchar" value="#arguments.hasFormData#">,
                <cfqueryparam cfsqltype="cf_sql_varchar" value="#cgi.script_name#">,
                <cfif len(trim(arguments.logName))>
                    <cfqueryparam cfsqltype="cf_sql_varchar" value="#arguments.logName#">
                <cfelse>
                    NULL
                </cfif>
            )
        </cfquery>

        <cfif NOT FileExists(outfile)>
            <cffile action="write" file="#outfile#" output="#arguments.logData#" mode="777">
        <cfelse>
            <cffile action="append" file="#outfile#" output="#arguments.logData#" mode="777">
        </cfif>

        <!--- <cfset writeLog(file="debuglog", text="✅ writeToLog completed successfully")> --->
        <cfcatch type="any">
            <!--- Failsafe logging --->
            <cfset writeLog(file="debuglog", text="❌ writeToLog error: #cfcatch.message# - #cfcatch.detail#")>
        </cfcatch>
    </cftry>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<!--- Returns a simulated form struct with a fieldNames -- used in writeToLog --->
<cffunction name="jsonData_ToFormStruct" access="public" returntype="void">
	<cfargument name="data" type="struct" required="yes">

	<cfset form.fieldNames = "">
	<cfloop collection="#arguments.data#" item="key">
		<cfset form[key] = arguments.data[key]>
		<cfif len(form.fieldNames)>
			<cfset form.fieldNames &= "," & key>
		<cfelse>
			<cfset form.fieldNames = key>
		</cfif>
	</cfloop>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="getParamsFromUrlString" returntype="Struct" output=false >
    <cfargument name="UrlString" type="String" required />
    <cfargument name="Separator" type="String" default="?" />
    <cfargument name="Delimiter" type="String" default="&" />
    <cfargument name="AssignOp"  type="String" default="=" />
    <cfargument name="EmptyVars" type="String" default="" />

    <cfset var QueryString = ListRest( ListFirst( Arguments.UrlString , '##' ) , Arguments.Separator ) />
	
    <cfset var Result = {} />

    <cfloop index="local.QueryPiece" list=#QueryString# delimiters="#Arguments.Delimiter#">

        <cfif NOT find(Arguments.AssignOp,QueryPiece)>
            <cfset Result[ UrlDecode( QueryPiece ) ] = Arguments.EmptyVars />
        <cfelse>
            <cfset Result[ UrlDecode( ListFirst(QueryPiece,Arguments.AssignOp) ) ]
                =  UrlDecode( ListRest(QueryPiece,Arguments.AssignOp,true) ) />
        </cfif>
    </cfloop>

    <cfreturn Result />
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<cfscript>
    // Function to rotate key
    function rotateKey() {
        var newKey = generateSecretKey("AES");
        var currentTime = now();
    
        // Insert the new key into the database with a timestamp
        queryExecute(
            "INSERT INTO encryption_keys (key_value, created_date) VALUES (:key_value, :created_date)",
            {key_value: {value: newKey, cfsqltype: "cf_sql_varchar"}, created_date: {value: currentTime, cfsqltype: "cf_sql_timestamp"}},
            {datasource: application.datasource}
        );
    
        return newKey;
    }

    // Function to encrypt data
    function encryptData(data) {
        var latestKeyQuery = queryExecute(
            "SELECT key_value FROM encryption_keys ORDER BY created_date DESC",
            {},
            {datasource: application.datasource, maxRows: 1}
        );
        var latestKey = latestKeyQuery.key_value;
        return encrypt(data, latestKey, "AES", "HEX");
    }
    
    // Function to decrypt data
    function decryptData(data, keyDate) {
        var keyQuery = queryExecute(
            "SELECT key_value FROM encryption_keys WHERE created_date <= :keyDate ORDER BY created_date DESC",
            {keyDate: {value: keyDate, cfsqltype: "cf_sql_timestamp"}},
            {datasource: application.datasource, maxRows: 1}
        );
        var key = keyQuery.key_value;
        return decrypt(data, key, "AES", "HEX");
    }
</cfscript>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
 <cffunction name="singularize" access="public" returntype="string">
    <cfargument name="word" type="string" required="true">
    
	<cfset var rules = [
        {regex="(s)$", replacement=""}, <!--- general rule for 's' at the end --->
        {regex="(ies)$", replacement="y"}, <!--- for words ending in 'ies' --->
        {regex="(oes)$", replacement="o"}, <!--- for words ending in 'oes' --->
        {regex="(ves)$", replacement="f"}, <!--- for words ending in 'ves' --->
        {regex="(men)$", replacement="man"}, <!--- for words ending in 'men' --->
        {regex="(children)$", replacement="child"}, <!--- special case for 'children' --->
        {regex="(mice)$", replacement="mouse"}, <!--- special case for 'mice' --->
        {regex="(geese)$", replacement="goose"}, <!--- special case for 'geese' --->
        {regex="(feet)$", replacement="foot"}, <!--- special case for 'feet' --->
        {regex="(teeth)$", replacement="tooth"}, <!--- special case for 'teeth' --->
        {regex="(people)$", replacement="person"} <!--- special case for 'people' --->
    ]>
    
    <cfset var i = 0>
    <cfset var rule = {}>

    <!--- Loop through the rules to find a match --->
    <cfloop index="i" from="1" to="#arrayLen(rules)#">
        <cfset rule = rules[i]>
        <cfif refindnocase(rule.regex, arguments.word)>
            <cfreturn rereplace(arguments.word, rule.regex, rule.replacement, "one")>
        </cfif>
    </cfloop>
    
    <!--- Return the original word if no rules match --->
    <cfreturn arguments.word>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="isDeptAllowed" access="public" returntype="boolean">
    <cfargument name="allowableDepartments" type="string" required="true">
	
	<cfset rc = false>
	<cfif NOT len(trim(arguments.allowableDepartments))>
		<cfset rc = true>
	<cfelse>
		<cfset allowedDepartmentsArray = ListToArray(arguments.allowableDepartments)>
		
		<cfif isdefined("session.userprofiledepartments")>
			<cfset myDepartments = session.userprofiledepartments>
			<cfif isdefined("session.impersonateDepartment") AND isNumeric(session.impersonateDepartment)>
				<cfset myDepartments = session.impersonateDepartment>
			</cfif>
			<cfset myDepartmentsArray = ListToArray(myDepartments)>
			
			<cfloop array="#myDepartmentsArray#" index="myDeptId">
				
				<cfif ArrayContains(allowedDepartmentsArray, myDeptId)>
					<cfset rc = true>
                    <cfbreak>
				</cfif>
			</cfloop>
		</cfif>
	</cfif>

    <cfreturn rc>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="isDeveloperDept" access="public" returntype="boolean">
   	
	<cfset rc = false>
	
	<cfset allowedDepartmentsArray = ListToArray('6')>
	
	<cfif isdefined("session.userprofiledepartments")>
		<cfset myDepartments = session.userprofiledepartments>
        <cfif isdefined("session.impersonateDepartment") AND Len(trim(session.impersonateDepartment))>
       		<cfset myDepartments = session.impersonateDepartment>
        </cfif>
		<cfset myDepartmentsArray = ListToArray(myDepartments)>
		
		<cfloop array="#myDepartmentsArray#" index="myDeptId">
            
            <cfif ArrayContains(allowedDepartmentsArray, myDeptId)>
                <cfset rc = true>
                <cfbreak>
            </cfif>

        </cfloop>
    </cfif>

    <cfreturn rc>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="isRoleAllowed" access="public" returntype="boolean">
    <cfargument name="allowableRoles" type="string" required="true">
	
	<cfset rc = false>
	<cfif NOT len(trim(arguments.allowableRoles))>
		<cfset rc = true>
	<cfelse>
		<cfset allowedRolesArray = ListToArray(arguments.allowableRoles)>
		
		<cfif isdefined("session.userprofileroles")>
			
			<cfset myRoles = session.userprofileroles>
			<cfif isdefined("session.impersonateRole") AND isNumeric(session.impersonateRole)>
				<cfset myRoles = session.impersonateRole>
			</cfif>
			<cfset myRolesArray = ListToArray(myRoles)>
		
			<cfloop array="#myRolesArray#" index="myRoleId">
				<cfif ArrayContains(allowedRolesArray, myRoleId)>
					<cfset rc = true>
                    <cfbreak>
				</cfif>
			</cfloop>
		</cfif>
	</cfif>
	
    <cfreturn rc>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="toProperCase" output="false" returnType="string">
	<cfargument name="inString" type="string" required="true" />

	<cfset returnString = rereplace(lcase(arguments.inString), "(\b\w)", "\u\1", "all")>
	<cfreturn returnString>
</cffunction> 
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="getMyPermissions" access="public" returntype="boolean" output="false" >

    <!--- QUERRY FOR PERMISSION RULES  GO IN HERE  --->
    <!--- Maybe by task, using session perms, roles, departments and userids ????? --->
    

    <!--- SHOULD RETURN CRUD (masked) so 
         0 (0000) is nothing
         1 (0001) is delete only
         2 (0010) is update only
         3 (0011) is update and delete
         4 (0100) is read only
         5 (0101) is read and delete
         6 (0110) is read and update
         7 (0111) is read, delete, update 
         8 (1000) is create only
         9 (1001) is create and delete 
        10 (1010) is create and read 
        11 (1011) is create, update and delete
        12 (1100) is create and update  
        13 (1101) is create, read and delete
        14 (1110) is create, read and update
        15 (1111) is create, read, update and delete 
    --->
    <cfset hasCreate = true>
    <cfset hasRead = true>
    <cfset hasUpdate = false>
    <cfset hasDelete = false>

    <cfset permissionMask = 0>

    <cfif hasCreate>
        <cfset permissionMask += 8>
    </cfif>
    <cfif hasRead>
        <cfset permissionMask += 4>
    </cfif>
    <cfif hasUpdate>
        <cfset permissionMask += 2>
    </cfif>
    <cfif hasDelete>
        <cfset permissionMask += 1>
    </cfif>

    <cfoutput>
        Permission Mask (Decimal): #permissionMask#<br>
        Permission Mask (Binary): #formatBaseN(permissionMask, 2)#
    </cfoutput>
  
    <cfreturn permissionMask>

</cffunction> 
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->

<cffunction name="queryToStruct" access="public" returntype="struct" output="false">
    <cfargument name="query" type="query" required="true">
    
    <cfset var result = {}>
    <cfset var columns = arguments.query.getColumnNames()>
    
    <cfloop query="arguments.query">
        <cfset var rowStruct = {}>
        <cfloop array="#columns#" index="column">
            <cfset rowStruct[column] = arguments.query[column][arguments.query.currentRow]>
        </cfloop>
        <cfset result[arguments.query.currentRow] = rowStruct>
    </cfloop>
    
    <cfreturn result>
</cffunction>

<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
<cffunction name="truncateSEOTitle" returntype="string" output="false">
    <cfargument name="title" type="string" required="true">
    <cfargument name="maxLength" type="numeric" required="false" default="60">
    <cfargument name="siteName" type="string" required="false" default="">
    
    <cfscript>
        // Clean the title and remove any extra whitespace
        var cleanTitle = trim(arguments.title);
        var suffix = arguments.siteName;
        var suffixLength = len(suffix);
        var maxMainTitleLength = arguments.maxLength - suffixLength;
        
        // Strip out any existing site name and separators for clean truncation
        cleanTitle = replaceNoCase(cleanTitle, suffix, "");
        cleanTitle = rereplaceNoCase(cleanTitle, "Article: |Blog: ", "", "All");
        
        // If main content is too long, truncate it
        if (len(cleanTitle) > maxMainTitleLength) {
            // Find the last space before cutoff
            var truncatedTitle = left(cleanTitle, maxMainTitleLength - 3); // -3 for "..."
            var lastSpacePos = find(" ", reverse(truncatedTitle));
            
            if (lastSpacePos) {
                truncatedTitle = left(truncatedTitle, len(truncatedTitle) - lastSpacePos);
            }
            
            return truncatedTitle & "...";
        }
        
        return cleanTitle & suffix;
    </cfscript>
</cffunction>
<!--- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --->
