# Lucee / CFML Documentation

## Overview
ColdFusion Markup Language (CFML) is a scripting language for web development that runs on the JVM. Lucee is an open-source CFML engine that provides high performance and modern features. This documentation covers CFML syntax and Lucee-specific features.

## Basic Syntax

### Tags vs Script Syntax

CFML supports both tag-based and script-based syntax:

#### Tag Syntax
```cfml
<cfset name = "John Doe">
<cfoutput>#name#</cfoutput>
<cfif age GT 18>
    <p>Adult</p>
<cfelse>
    <p>Minor</p>
</cfif>
```

#### Script Syntax (CFScript)
```cfml
<cfscript>
    name = "John Doe";
    writeOutput(name);
    if (age > 18) {
        writeOutput("<p>Adult</p>");
    } else {
        writeOutput("<p>Minor</p>");
    }
</cfscript>
```

## Variables and Data Types

### Variable Scopes

| Scope | Description | Persistence |
|-------|-------------|-------------|
| `variables` | Page/component scope | Current request |
| `request` | Request scope | Current request |
| `session` | User session | Session timeout |
| `application` | Application scope | Application lifetime |
| `server` | Server scope | Server lifetime |
| `form` | Form submissions | Current request |
| `url` | URL parameters | Current request |
| `cgi` | CGI variables | Current request |
| `cookie` | Browser cookies | Cookie expiration |
| `client` | Client variables | 90 days default |
| `arguments` | Function arguments | Function execution |
| `local` | Function local scope | Function execution |
| `this` | Component public scope | Component instance |

### Data Types

```cfml
<!--- String --->
<cfset myString = "Hello World">

<!--- Number --->
<cfset myNumber = 42>
<cfset myFloat = 3.14>

<!--- Boolean --->
<cfset myBoolean = true>

<!--- Date --->
<cfset myDate = now()>
<cfset specificDate = createDate(2024, 1, 15)>

<!--- Array --->
<cfset myArray = ["apple", "banana", "orange"]>
<cfset myArray = arrayNew(1)>
<cfset arrayAppend(myArray, "grape")>

<!--- Struct --->
<cfset myStruct = {
    name: "John",
    age: 30,
    email: "john@example.com"
}>
<cfset myStruct = structNew()>
<cfset myStruct.city = "New York">

<!--- Query --->
<cfset myQuery = queryNew("id,name,email", "integer,varchar,varchar")>
<cfset queryAddRow(myQuery, {id: 1, name: "John", email: "john@example.com"})>
```

## Database Operations

### Query Execution

```cfml
<!--- Basic Query --->
<cfquery name="getUsers" datasource="myDatasource">
    SELECT id, name, email
    FROM users
    WHERE active = 1
    ORDER BY name
</cfquery>

<!--- Query with Parameters (SQL Injection Safe) --->
<cfquery name="getUser" datasource="myDatasource">
    SELECT * FROM users
    WHERE id = <cfqueryparam value="#url.id#" cfsqltype="cf_sql_integer">
    AND email = <cfqueryparam value="#form.email#" cfsqltype="cf_sql_varchar">
</cfquery>

<!--- Insert with Generated Key Retrieval --->
<cfquery name="insertUser" datasource="myDatasource" result="insertResult">
    INSERT INTO users (name, email, created_date)
    VALUES (
        <cfqueryparam value="#form.name#" cfsqltype="cf_sql_varchar">,
        <cfqueryparam value="#form.email#" cfsqltype="cf_sql_varchar">,
        <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
    )
</cfquery>
<cfset newUserId = insertResult.generatedKey>

<!--- Update Query --->
<cfquery datasource="myDatasource">
    UPDATE users 
    SET 
        name = <cfqueryparam value="#form.name#" cfsqltype="cf_sql_varchar">,
        modified_date = <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
    WHERE 
        id = <cfqueryparam value="#form.id#" cfsqltype="cf_sql_integer">
</cfquery>

<!--- Delete Query --->
<cfquery datasource="myDatasource">
    DELETE FROM users
    WHERE id = <cfqueryparam value="#url.id#" cfsqltype="cf_sql_integer">
</cfquery>
```

### Query of Queries (QoQ)

```cfml
<!--- Query existing query resultset --->
<cfquery name="filteredUsers" dbtype="query">
    SELECT * FROM getUsers
    WHERE name LIKE '%smith%'
    ORDER BY email
</cfquery>
```

### CFQueryParam Types

| Type | Description |
|------|-------------|
| `cf_sql_varchar` | String/Text |
| `cf_sql_integer` | Integer |
| `cf_sql_bigint` | Large Integer |
| `cf_sql_decimal` | Decimal |
| `cf_sql_float` | Float |
| `cf_sql_date` | Date only |
| `cf_sql_time` | Time only |
| `cf_sql_timestamp` | Date and Time |
| `cf_sql_bit` | Boolean |
| `cf_sql_longvarchar` | Long text/CLOB |

## Functions

### User-Defined Functions

```cfml
<!--- Tag-based Function --->
<cffunction name="calculateTax" returntype="numeric" access="public">
    <cfargument name="amount" type="numeric" required="true">
    <cfargument name="rate" type="numeric" default="0.08">
    
    <cfset var tax = arguments.amount * arguments.rate>
    <cfreturn tax>
</cffunction>

<!--- Script-based Function --->
<cfscript>
function getUserFullName(required string firstName, required string lastName) {
    return arguments.firstName & " " & arguments.lastName;
}

// Modern arrow function (Lucee 5+)
var sum = (a, b) => a + b;

// Function with multiple return types
function processData(required any data) {
    if (isArray(arguments.data)) {
        return arrayLen(arguments.data);
    } else if (isStruct(arguments.data)) {
        return structCount(arguments.data);
    } else {
        return len(arguments.data);
    }
}
</cfscript>
```

### Built-in Functions

#### String Functions
```cfml
<cfset upper = uCase("hello")>                    <!--- HELLO --->
<cfset lower = lCase("HELLO")>                    <!--- hello --->
<cfset trimmed = trim("  hello  ")>               <!--- hello --->
<cfset length = len("hello")>                     <!--- 5 --->
<cfset substring = mid("hello", 2, 3)>            <!--- ell --->
<cfset replaced = replace("hello", "l", "L", "all")> <!--- heLLo --->
<cfset found = find("ll", "hello")>               <!--- 3 --->
<cfset list = listAppend("a,b", "c")>            <!--- a,b,c --->
```

#### Array Functions
```cfml
<cfset arr = [1, 2, 3]>
<cfset arrayAppend(arr, 4)>
<cfset arrayPrepend(arr, 0)>
<cfset sorted = arraySort(arr, "numeric")>
<cfset filtered = arrayFilter(arr, function(item) { return item > 2; })>
<cfset mapped = arrayMap(arr, function(item) { return item * 2; })>
<cfset found = arrayFind(arr, 3)>
<cfset exists = arrayContains(arr, 3)>
```

#### Structure Functions
```cfml
<cfset struct = {name: "John", age: 30}>
<cfset structInsert(struct, "email", "john@example.com")>
<cfset structDelete(struct, "age")>
<cfset exists = structKeyExists(struct, "name")>
<cfset keys = structKeyArray(struct)>
<cfset values = structValueArray(struct)>
<cfset copied = structCopy(struct)>           <!--- Shallow copy --->
<cfset deepCopy = duplicate(struct)>          <!--- Deep copy --->
```

#### Date Functions
```cfml
<cfset currentDate = now()>
<cfset date = createDate(2024, 1, 15)>
<cfset dateTime = createDateTime(2024, 1, 15, 10, 30, 0)>
<cfset formatted = dateFormat(now(), "mm/dd/yyyy")>
<cfset timeFormatted = timeFormat(now(), "HH:mm:ss")>
<cfset added = dateAdd("d", 7, now())>        <!--- Add 7 days --->
<cfset diff = dateDiff("d", date1, date2)>    <!--- Days between dates --->
<cfset year = year(now())>
<cfset month = month(now())>
<cfset day = day(now())>
```

## Components (CFCs)

### Component Definition

```cfml
<!--- Person.cfc --->
<cfcomponent displayname="Person" hint="Person component">
    
    <!--- Properties (Lucee/CF11+) --->
    <cfproperty name="firstName" type="string">
    <cfproperty name="lastName" type="string">
    <cfproperty name="age" type="numeric">
    
    <!--- Constructor --->
    <cffunction name="init" returntype="Person" access="public">
        <cfargument name="firstName" type="string" required="true">
        <cfargument name="lastName" type="string" required="true">
        <cfargument name="age" type="numeric" default="0">
        
        <cfset this.firstName = arguments.firstName>
        <cfset this.lastName = arguments.lastName>
        <cfset this.age = arguments.age>
        
        <cfreturn this>
    </cffunction>
    
    <!--- Public Method --->
    <cffunction name="getFullName" returntype="string" access="public">
        <cfreturn this.firstName & " " & this.lastName>
    </cffunction>
    
    <!--- Private Method --->
    <cffunction name="calculateBirthYear" returntype="numeric" access="private">
        <cfreturn year(now()) - this.age>
    </cffunction>
    
</cfcomponent>
```

### Component Usage

```cfml
<!--- Create Instance --->
<cfset person = createObject("component", "Person").init("John", "Doe", 30)>
<cfset person = new Person("John", "Doe", 30)>  <!--- CF9+ syntax --->

<!--- Call Methods --->
<cfset fullName = person.getFullName()>
<cfoutput>#fullName#</cfoutput>
```

## Control Structures

### Conditionals

```cfml
<!--- If/ElseIf/Else --->
<cfif age GTE 18>
    <p>Adult</p>
<cfelseif age GTE 13>
    <p>Teenager</p>
<cfelse>
    <p>Child</p>
</cfif>

<!--- Switch/Case --->
<cfswitch expression="#userType#">
    <cfcase value="admin">
        <p>Administrator Access</p>
    </cfcase>
    <cfcase value="user,guest">
        <p>Limited Access</p>
    </cfcase>
    <cfdefaultcase>
        <p>No Access</p>
    </cfdefaultcase>
</cfswitch>

<!--- Script Syntax --->
<cfscript>
if (age >= 18) {
    writeOutput("Adult");
} else if (age >= 13) {
    writeOutput("Teenager");
} else {
    writeOutput("Child");
}

switch(userType) {
    case "admin":
        writeOutput("Administrator");
        break;
    case "user":
    case "guest":
        writeOutput("Limited");
        break;
    default:
        writeOutput("None");
}
</cfscript>
```

### Loops

```cfml
<!--- Array Loop --->
<cfloop array="#myArray#" index="item">
    <cfoutput>#item#</cfoutput>
</cfloop>

<!--- Collection/Structure Loop --->
<cfloop collection="#myStruct#" item="key">
    <cfoutput>#key#: #myStruct[key]#</cfoutput>
</cfloop>

<!--- Query Loop --->
<cfloop query="getUsers">
    <cfoutput>#getUsers.name# - #getUsers.email#</cfoutput>
</cfloop>

<!--- Index Loop --->
<cfloop index="i" from="1" to="10" step="2">
    <cfoutput>#i#</cfoutput>
</cfloop>

<!--- List Loop --->
<cfloop list="apple,banana,orange" index="fruit" delimiters=",">
    <cfoutput>#fruit#</cfoutput>
</cfloop>

<!--- While Loop (Script) --->
<cfscript>
counter = 1;
while (counter <= 10) {
    writeOutput(counter);
    counter++;
}

// For loop
for (i = 1; i <= 10; i++) {
    writeOutput(i);
}

// For-in loop
for (item in myArray) {
    writeOutput(item);
}
</cfscript>
```

## Error Handling

### Try/Catch

```cfml
<cftry>
    <!--- Code that might throw an error --->
    <cfquery name="getData" datasource="myDS">
        SELECT * FROM users
    </cfquery>
    
<cfcatch type="database">
    <cflog text="Database error: #cfcatch.message#" file="errors">
    <p>Database error occurred. Please try again.</p>
</cfcatch>

<cfcatch type="any">
    <cflog text="Error: #cfcatch.message#" file="errors">
    <p>An error occurred: #cfcatch.message#</p>
</cfcatch>

<cffinally>
    <!--- Cleanup code that always runs --->
</cffinally>
</cftry>

<!--- Script syntax --->
<cfscript>
try {
    // risky code
    result = riskyOperation();
} catch (DatabaseException e) {
    writeLog(text=e.message, file="errors");
} catch (any e) {
    writeOutput("Error: " & e.message);
} finally {
    // cleanup
}
</cfscript>
```

### Custom Exceptions

```cfml
<!--- Throw custom exception --->
<cfthrow type="CustomError" 
         message="Invalid user data" 
         detail="Email address is required">

<!--- Script syntax --->
<cfscript>
if (not isValid("email", form.email)) {
    throw(type="ValidationError", message="Invalid email address");
}
</cfscript>
```

## File Operations

### File Handling

```cfml
<!--- Read File --->
<cffile action="read" 
        file="#expandPath('./data.txt')#" 
        variable="fileContent">

<!--- Write File --->
<cffile action="write" 
        file="#expandPath('./output.txt')#" 
        output="#content#">

<!--- Append to File --->
<cffile action="append" 
        file="#expandPath('./log.txt')#" 
        output="#logEntry#">

<!--- Upload File --->
<cffile action="upload" 
        fileField="uploadFile" 
        destination="#expandPath('./uploads/')#" 
        nameConflict="makeunique"
        accept="image/jpeg,image/png,application/pdf">

<!--- Delete File --->
<cffile action="delete" 
        file="#expandPath('./temp.txt')#">

<!--- Copy File --->
<cffile action="copy" 
        source="#expandPath('./source.txt')#" 
        destination="#expandPath('./backup/source.txt')#">

<!--- Move/Rename File --->
<cffile action="move" 
        source="#expandPath('./old.txt')#" 
        destination="#expandPath('./new.txt')#">
```

### Directory Operations

```cfml
<!--- List Directory --->
<cfdirectory action="list" 
             directory="#expandPath('./uploads/')#" 
             name="fileList" 
             filter="*.pdf">

<!--- Create Directory --->
<cfdirectory action="create" 
             directory="#expandPath('./newFolder/')#">

<!--- Delete Directory --->
<cfdirectory action="delete" 
             directory="#expandPath('./tempFolder/')#" 
             recurse="true">

<!--- Loop through files --->
<cfloop query="fileList">
    <cfoutput>
        #fileList.name# - #fileList.size# bytes - #fileList.dateLastModified#
    </cfoutput>
</cfloop>
```

## HTTP Requests

### CFHTTP

```cfml
<!--- GET Request --->
<cfhttp url="https://api.example.com/data" method="GET" result="response">
    <cfhttpparam type="header" name="Authorization" value="Bearer #token#">
    <cfhttpparam type="url" name="limit" value="100">
</cfhttp>

<cfif response.statusCode EQ "200 OK">
    <cfset data = deserializeJSON(response.fileContent)>
</cfif>

<!--- POST Request --->
<cfhttp url="https://api.example.com/users" method="POST" result="response">
    <cfhttpparam type="header" name="Content-Type" value="application/json">
    <cfhttpparam type="body" value="#serializeJSON(userData)#">
</cfhttp>

<!--- File Upload --->
<cfhttp url="https://api.example.com/upload" method="POST">
    <cfhttpparam type="file" name="document" file="#expandPath('./document.pdf')#">
    <cfhttpparam type="formfield" name="title" value="My Document">
</cfhttp>
```

## Session Management

### Application.cfc

```cfml
<cfcomponent>
    <cfset this.name = "MyApplication">
    <cfset this.applicationTimeout = createTimeSpan(1,0,0,0)> <!--- 1 day --->
    <cfset this.sessionManagement = true>
    <cfset this.sessionTimeout = createTimeSpan(0,0,30,0)> <!--- 30 minutes --->
    <cfset this.clientManagement = false>
    <cfset this.setClientCookies = true>
    <cfset this.datasource = "myDatasource">
    
    <cffunction name="onApplicationStart" returntype="boolean">
        <cfset application.config = {
            siteName: "My Site",
            adminEmail: "admin@example.com",
            uploadPath: expandPath("./uploads/")
        }>
        <cfreturn true>
    </cffunction>
    
    <cffunction name="onSessionStart">
        <cfset session.isLoggedIn = false>
        <cfset session.userID = 0>
        <cfset session.startTime = now()>
    </cffunction>
    
    <cffunction name="onRequestStart" returntype="boolean">
        <cfargument name="targetPage" type="string" required="true">
        
        <!--- Check for login on admin pages --->
        <cfif findNoCase("/admin/", arguments.targetPage) AND NOT session.isLoggedIn>
            <cflocation url="/login.cfm" addtoken="false">
        </cfif>
        
        <cfreturn true>
    </cffunction>
    
    <cffunction name="onError">
        <cfargument name="exception" required="true">
        <cfargument name="eventName" type="string" required="true">
        
        <cflog text="#arguments.exception.message#" file="errors">
        <cfinclude template="/error.cfm">
    </cffunction>
</cfcomponent>
```

## JSON Handling

```cfml
<!--- Serialize to JSON --->
<cfset myData = {
    name: "John",
    age: 30,
    hobbies: ["reading", "gaming"]
}>
<cfset jsonString = serializeJSON(myData)>

<!--- Deserialize from JSON --->
<cfset jsonData = '{"name":"John","age":30}'>
<cfset structData = deserializeJSON(jsonData)>

<!--- JSON output with proper content type --->
<cfcontent type="application/json">
<cfoutput>#serializeJSON(responseData)#</cfoutput>
```

## Regular Expressions

```cfml
<!--- Pattern matching --->
<cfset isEmail = reFind("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email)>

<!--- Find with subexpressions --->
<cfset result = reFind("([0-9]{3})-([0-9]{3})-([0-9]{4})", phone, 1, true)>
<cfif result.pos[1] GT 0>
    <cfset areaCode = mid(phone, result.pos[2], result.len[2])>
</cfif>

<!--- Replace --->
<cfset cleaned = reReplace(text, "[^A-Za-z0-9]", "", "all")>

<!--- Replace with backreferences --->
<cfset formatted = reReplace(date, "([0-9]{4})-([0-9]{2})-([0-9]{2})", "\2/\3/\1", "one")>
```

## Lucee-Specific Features

### Member Functions (Lucee 4.5+)

```cfml
<!--- String member functions --->
<cfset upper = "hello".uCase()>
<cfset trimmed = "  hello  ".trim()>
<cfset replaced = "hello".replace("l", "L", "all")>

<!--- Array member functions --->
<cfset arr = [1, 2, 3]>
<cfset arr.append(4)>
<cfset filtered = arr.filter(function(i) { return i > 2; })>
<cfset mapped = arr.map(function(i) { return i * 2; })>

<!--- Struct member functions --->
<cfset struct = {name: "John"}>
<cfset struct.insert("age", 30)>
<cfset keys = struct.keyArray()>
```

### Lambda Expressions

```cfml
<cfscript>
// Arrow functions
sum = (a, b) => a + b;
isEven = n => n % 2 == 0;

// Array operations with lambdas
numbers = [1, 2, 3, 4, 5];
evens = numbers.filter(n => n % 2 == 0);
doubled = numbers.map(n => n * 2);
total = numbers.reduce((acc, n) => acc + n, 0);
</cfscript>
```

### Parallel Processing

```cfml
<!--- Parallel array iteration --->
<cfset results = arrayEach(largeArray, function(item) {
    return processItem(item);
}, true)> <!--- true = parallel execution --->

<!--- Thread management --->
<cfthread name="thread1" action="run">
    <!--- Async operation --->
</cfthread>

<cfthread action="join" name="thread1" timeout="5000">
```

### Caching

```cfml
<!--- Cache a query --->
<cfquery name="getUsers" datasource="myDS" cachedwithin="#createTimeSpan(0,1,0,0)#">
    SELECT * FROM users
</cfquery>

<!--- Cache a fragment --->
<cfcache action="cache" timeout="#createTimeSpan(0,0,30,0)#">
    <!--- Expensive content generation --->
</cfcache>

<!--- Clear cache --->
<cfcache action="flush">
```

## Best Practices

1. **Always use `cfqueryparam`** for database queries to prevent SQL injection
2. **Use `var` or `local` scope** in functions to prevent variable leaking
3. **Enable request timeout** to prevent long-running requests
4. **Use structured exception handling** with try/catch blocks
5. **Implement proper session management** with secure session cookies
6. **Use component inheritance** and composition for code reuse
7. **Cache frequently accessed data** to improve performance
8. **Validate all user input** before processing
9. **Use semantic variable and function names**
10. **Comment complex logic** and document components

## Performance Tips

1. **Query Optimization**
   - Use stored procedures for complex queries
   - Limit SELECT columns to only needed fields
   - Use query caching for static data

2. **Code Optimization**
   - Use `cfqueryparam` for better query plan caching
   - Minimize use of `evaluate()` and `iif()`
   - Use member functions for cleaner code

3. **Memory Management**
   - Clear large variables when done: `structClear(largeStruct)`
   - Use streaming for large file operations
   - Monitor JVM memory settings

## Resources

- [Lucee Documentation](https://docs.lucee.org/)
- [CFML Reference](https://cfdocs.org/)
- [Lucee Forum](https://dev.lucee.org/)
- [CFML Slack](https://cfml.slack.com/)
- [Learn CF in a Week](https://learncfinaweek.com/)
- [CF Cookbook](https://cfcookbook.com/)