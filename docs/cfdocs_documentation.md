# CFDocs - ColdFusion (CFML) Documentation

CFDocs is a community-maintained CFML reference tool providing fast, easy-to-use documentation for ColdFusion Markup Language tags and functions.

## Installation and Server Management

### Installing ColdFusion 11

#### UNIX Installation
```bash
# Change file permissions before installation
chmod 777 ColdFusion_11_WWEJ_solaris64.bin

# Start installer
./<filename>

# Start installer with GUI
./<filename> -i gui
```

#### Managing ColdFusion Server

**UNIX/Linux/macOS:**
```bash
# Start server
./coldfusion start

# Stop server
./coldfusion stop

# Restart server
./coldfusion restart

# Check status
./coldfusion status
```

**Windows:**
```batch
coldfusion.exe -start -console
coldfusion.exe -stop -console
coldfusion.exe -restart -console
```

#### Uninstalling ColdFusion (UNIX)
```bash
cd cf_root/uninstall
./uninstall.sh
```

### ColdFusion Directory Structure

Default ColdFusion 11 installation creates the following structure:

```
_cfusion_:
  bin: Programs for starting, stopping, and viewing information for ColdFusion
  cache: Repository for temporary files from ColdFusion
  cfx: Sample C++ and Java CFX files with their supporting files
  charting: Files for the ColdFusion graphing and charting engine
  CustomTags: Repository for your custom tags
  db: The sample Apache Derby databases for all platforms
  gateway: Files for ColdFusion event gateways
  jetty: Solr configuration files and files related to remote instance start and stop
  jintegra: (Windows only) JIntegra programs, libraries, and other supporting files
  jnbridge: Files for .NET Integration Services
  lib: JAR, XML, property, and other files that are the foundation of ColdFusion
  logs: Repository for ColdFusion log files
```

## CFScript Syntax

### Loops

#### For Loop
```cfml
for (i=1; i <= 5; i++) {
    // all statements in the block are looped over
    result = i * 2;
    writeOutput(result);
}
```

#### While Loop
```cfml
while (condition) {
    // statements
}
```

#### Query Loop
```cfml
q = queryNew("id,data", "integer,varchar", [  [11, "aa"], [22, "bb"], [33, "cc"]  ] );
for (row in q) {
    writeOutput("#q.currentRow#:#row.id#:#row.data#;");
    //result:   1:11:aa;2:22:bb;3:33:cc;
}
```

#### CF11+ Query Loop with cfloop
```cfml
cfloop(query=q, group="fk") {
    writeOutput("<strong>#fk#</strong>");
}
```

### Conditional Statements

```cfml
count = 10;
if (count > 20) {
    writeOutput(count);
} else if (count == 8) {
    writeOutput(count);
} else {
    writeOutput(count);
}
```

### Loop Control

#### Break and Continue
```cfml
for (row in q) {
    if (row.skip) {
        continue;
    }
    //do stuff...
}

for (row in q) {
    if (q.currentRow > 5) {
        break;
    }
    //process rows 1-5
}
```

### Threading

#### CF9 vs CF11+ Syntax
```cfml
//CF9 syntax
thread action="run" name="testName" {
   thread.test = "CFML";
}

//CF11 syntax
cfthread( action="run", name="testName") {
   thread.test = "CFML";
}
```

### Invoking Tags in CFScript

```cfml
cfexampletag (attrib=1, attr2=2);
{
    // First child tag having attributes in the parenthesis (Optional)
    cfexamplechild (child_attr1='cv1', child_attr2='cv2');
    {
        // Nested child tag
        cfexamplegrandchild (name="bob");
    }
    // Second child of parent tag
    cfexampleotherchild (child2_attr1='cv1', child2_attr2='cv2');
}
```

### Custom Tags in CFScript
```cfml
cf_myCustomTag(myArg="x", otherArg="y");
```

### Tags Not Directly Supported in CFScript
```cfml
<cfscript> (infinite loop :)
<cfoutput> (use writeOutput() instead)
<cfdump> (use writeDump() instead)
<cfinvoke> (use invoke() instead)
<cfinvokeargument>
<cfobject> (use createObject instead)
```

## Operators

### Elvis Operator (?:)

#### Basic Usage
```cfml
myDisplayName = userName ?: "Anonymous";
```

#### Ternary Operator
```cfml
result = isNumeric(17) ? "it's numeric" : "no it isn't"; // "it's numeric"
result = isNumeric("nineteen") ? "it's numeric" : "no it isn't"; // "no it isn't"
```

#### Nested Ternary (Discouraged)
```cfml
result = stage1.firstOperand ? stage1.secondOperand : stage2.firstOperand ? stage2.secondOperand : stage1.thirdOperand;
value = "nineteen";
result = isNumeric(value) ? "it's numeric" : (reFind("[A-Za-z]",value) > 0) ? "it's alphabetic" : "it's neither"; // "it's alphabetic"
```

### Concatenation Operator (&)
```cfml
name = name & " Jr.";
```

## Data Structures

### Arrays and Structs

#### Implicit vs. Explicit Initialization
```cfml
arr = []; // implicit
// is the same as
arr = arrayNew(1);

unorderedStruct = {};
orderedStruct = [:];
// is the same as
unorderedStruct = structNew();
orderedStruct = structNew('ordered');
```

#### Member Functions vs. Standard Functions
```cfml
// The standard way
var myArray = arrayNew(1);
arrayAppend(myArray, "objec_new");
arraySort(myArray, "ASC");

// The member way
myArray.append("objec_new");
myArray.sort("ASC");
```

#### Chaining Member Functions
```cfml
s = "the";
s = s.listAppend("quick brown fox", " ")
         .listAppend("jumps over the lazy dog", " ")
         .uCase()
         .reverse();
```

### String Slicing (CF2018 Update 5+)

```cfml
myString = "This is my string. I love CFDocs!";
writeOutput(myString[1]); // Returns T // First character from start of string.
writeOutput(myString[-1]); // Returns ! // First character from end of string.
writeOutput(myString[20:28]); // Returns I love CF
writeOutput(myString[-20,-10]); // Returns ring. I lov
writeOutput(myString[1,-10]); // Returns This is my string. I lov
writeOutput(myString[1:]); // Returns This is my string. I love CFDocs! // Full string from position 1 to end.
writeOutput(myString[:10]); // Returns This is my  // String from position 1 to position 10.
writeOutput(myString[5:25:5]); // Returns yiI  // Every 5th character from position 5 to 25.
writeOutput(myString[::2]); // Returns Ti sm tig oeCDc!  // Every other character in the string.
```

## Scopes

### URL Scope
```cfml
<cfoutput>
    You're looking at #URL.view#'s page #URL.page# in #URL.mode# mode
    <cfif structKeyExists(URL,'start')>
        Start with letter: #URL.start#
    </cfif>
</cfoutput>
```

## Application Management

### Application.cfc Structure

#### Basic Application Setup
```cfml
component {
    this.name = "myApplication";

    function onApplicationStart() {
        application.something = "otherthing";
    }
}
```

#### Java Settings (CF10+/Lucee 4.5+)
```cfml
component {
    this.name = "example";
    this.javaSettings = {
        loadPaths = ["/path/to/jarFile.jar"]
    };
}
```

### Application Scope Thread Safety
```cfml
// Unsafe - can cause data corruption
application.counter += 1;

// Safe - uses locking
lock scope="application" timeout="1" type="exclusive" {
    application.counter += 1;
}
```

## Closures

### Basic Closure Example
```cfml
function helloTranslator(String helloWord) {
    return function(String name) {
        return "#helloWord#, #name#";
    };
}

helloInHindi = helloTranslator("Namaste");
helloInFrench = helloTranslator("Bonjour");
writeOutput(helloInHindi("Anna"));
//closure is formed.
//Prints Namaste, Anna.
writeOutput("<br>");
writeOutput(helloInFrench("John"));
//Prints Bonjour, John.
```

### Assigning Closures to Variables
```cfml
var c2 = function () {..}

hello = function (arg1) {
    writeOutput("Hello " & arg1);
};
hello("Mark");
```

## First-Class Functions

### Dynamic Function Selection
```cfml
function convertArray(array array, string caseTo) {
    caseConverterFunction = getConvertFunction(caseTo);
    for (var i=1; i <= arrayLen(array); i++) {
        array[i] = caseConverterFunction(array[i]);
    }
    return array;
}

function getConvertFunction(string caseType) {
    if (caseType == 'lower') return lCase;
    return uCase;
}

results = {
    "lower" = convertArray(['One', 'Two', 'Three'], 'lower'),
    "upper" = convertArray(['One', 'Two', 'Three'], 'upper')
};

writeDump(results);
```

## Object Creation and Instantiation

### Using 'new' Operator
```cfml
pet = new Dog( "fido" );

<cfset pet = new Dog( breed="pitbull", name="hank" )>

pet = new Dog( breed="pitbull", name="hank" );
```

## Java Integration

### Creating Java Objects
```cfml
// Static method invocation
javaSystem = createObject("java", "java.lang.System");
currentTime = javaSystem.currentTimeMillis();
writeOutput(currentTime);

// Runtime access
runtime = createObject("java", "java.lang.Runtime").getRuntime();
writeOutput( runtime.availableProcessors() );

// Object instantiation with constructor
currentFile = createObject("java", "java.io.File").init( getCurrentTemplatePath() );
writeOutput( currentFile.lastModified() );

// Type casting with javaCast
integerObject = createObject("java", "java.lang.Integer");
maxInt = integerObject.max(javaCast("int", 5), javaCast("int", 6));
```

## Security

### Encryption

#### Generate AES Keys
```cfml
// generate a 128 bit AES encryption key
writeOutput( generateSecretKey( 'AES' ) );

// generate a 256 bit AES encryption key CF10+ Lucee4.5+
writeOutput( generateSecretKey( 'AES', 256 ) );
```

#### AES/CBC/PKCS5Padding Encryption
```cfml
myString = 'dog';
myKey = 'ITRkCTb/XMtGT0g99WUkKak/hhNvPml3k+UbsVDqSBE=';
myAlgorithm = 'AES/CBC/PKCS5Padding';
myEncoding = 'HEX';
encString = encrypt( myString, myKey, myAlgorithm, myEncoding );
writeOutput( encString );
```

#### Multi-Pass Encryption for Consistent Lookup
```cfml
myUsername = 'bob@bob.com';
myKey1 = 'RQr9IRygGQtguVEHvKh4WLgs5wz3V+BZIq82GKM5FrI=';
myAlgorithm1 = 'AES';
myEncoding1 = 'HEX';
myKey2 = '7SlPIgphVuR8sTGjBdKHBUqw2wss1XKwz5vYZXn7TY0=';
myAlgorithm2 = 'BLOWFISH';
myEncoding2 = 'BASE64';
myKey3 = 'zZYZVmsNFMqZcz0SzKMGPtCixdP9CWfmV3/xu9cwCRA=';
myAlgorithm3 = 'AES';
myEncoding3 = 'HEX';
encUsername = encrypt( myUsername, myKey1, myAlgorithm1, myEncoding1 );
encUsername = encrypt( encUsername, myKey2, myAlgorithm2, myEncoding2 );
encUsername = encrypt( encUsername, myKey3, myAlgorithm3, myEncoding3 );
writeOutput( encUsername );
```

### Parameter Obfuscation

#### Obfuscating URL Parameters
```cfml
<a href="Profile.cfm?v#hash( 'userId', 'SHA-384', 'UTF-8', 500 )#=#local.userId#
        &amp;v#hash( 'name', 'SHA-384', 'UTF-8', '1000' )#=#local.firstName#
        &amp;v#hash( 'departmentId', 'SHA-384', 'UTF-8', 750 )=#local.departmentId#">Edit Profile</a>
```

#### Retrieving Obfuscated URL Parameters
```cfml
param name="URL['v' & hash( 'userId', 'SHA-384', 'UTF-8', 500 )]" default="0";
param name="URL['v' & hash( 'name', 'SHA-384', 'UTF-8', 1000 )]" default="";
param name="URL['v' & hash( 'departmentId', 'SHA-384', 'UTF-8', 750 )]" default="0";
```

#### Obfuscating Form Fields
```cfml
<input type="hidden" name="ff#hash( 'userId', 'SHA-512', 'UTF-8', 825 )#" value="911" />
```

#### Retrieving Obfuscated Form Fields
```cfml
param name="FORM['ff' & hash( 'userId', 'SHA-512', 'UTF-8', 825 )]" default="0";
```

#### Encrypting URL Parameters
```cfml
myKey = 'Ng12PCeRET7ESEfUqwJCA2TgWh3wadBk/SDx10U/8lI=';
myAlgorithm = 'AES/CBC/PKCS5Padding';
myEncoding = 'HEX';
<a href="Profile.cfm?v#hash( 'userId', 'SHA-384', 'UTF-8', 500 )#=#encrypt( local.userId, myKey, myAlgorithm, myEncoding )#
&amp;v#hash( 'name', 'SHA-384', 'UTF-8', '1000' )#=#encrypt( local.firstName, myKey, myAlgorithm, myEncoding )#
&amp;v#hash( 'departmentId', 'SHA-384', 'UTF-8', 750 )=#encrypt( local.departmentId, myKey, myAlgorithm, myEncoding )#">Edit Profile</a>
```

#### Encrypting Hidden Form Fields
```cfml
myKey = 'tf0wcU7556DTt0ftUSkWOZlk82FkL7acSCnsCuWPHZ8=';
myAlgorithm = 'BLOWFISH/CBC/PKCS5Padding';
myEncoding = 'HEX';

writeOutput( "<input type=\"hidden\" name=\"ff#hash( 'userId', 'SHA-512', 'UTF-8', 825 )#\" value=\"#encrypt( local.userId, myKey, myAlgorithm, myEncoding )#\" />" );
```

### Session Management

#### Cookie Name Obfuscation
```cfml
// Example obfuscated cookie names
__ga_tracking_beacon_
__#hash( 'some_cookie_name', 'SHA-256', 'UTF-8', 25 )#
```

#### Session Timeout Configuration
```cfml
// set number of minutes before a session is timed out
application.timeoutMinutes = 30; // 30 minutes
```

#### Session Cookie Validation
```cfml
// we're not, check if the session cookie is defined
if ( !structKeyExists( cookie, application.cookieName ) ) {
    // it isn't, redirect to the login page
    variables.fw.redirect( action = 'main.login', queryString = "msg=501" );
}
```

### Hash Function API Reference
```
hash(string: String, algorithm: String, encoding: String, iterations: Integer): String
  string: The input string to be hashed (e.g., original parameter name).
  algorithm: The hashing algorithm to use (e.g., 'SHA-384', 'SHA-512').
  encoding: The character encoding for the input string (e.g., 'UTF-8').
  iterations: The number of hashing iterations to perform, increasing computational cost for attackers.
```

### SecurityService.cfc API
```
SecurityService.cfc:
  dataEnc(string: string, scope: string)
    string: The data string to encrypt.
    scope: The scope for encryption (e.g., 'URL', 'FORM', 'COOKIE', 'DATABASE').
    Returns: Encrypted string.
  dataDec(string: string, scope: string)
    string: The encrypted string to decrypt.
    scope: The scope used for encryption (e.g., 'URL', 'FORM', 'COOKIE', 'DATABASE').
    Returns: Decrypted string.
```

## Testing with TestBox

### BDD Style Tests
```cfml
component extends="testbox.system.BaseSpec" {
    function run() {
        describe("A sweet suite", function() {
            it("contains spec with an awesome expectation", function() {
                expect( true ).toBeTrue(); 
            });
        });
    }
}
```

### xUnit Style Tests
```cfml
component displayName="My Sweet Suite" extends="testbox.system.BaseSpec" {
    function testSomething() {
        var something = true;
        $assert.isTrue(something);
        $assert.notIsEmpty(something);
    }
}
```

### Common Assertion Methods
```cfml
//assert that value is true
$assert.isTrue(value, message);

//assert that value is false
$assert.isFalse(value, message);

//assert that expected is equal actual, no case is required.
$assert.isEqual(expected, actual, message);

//assert that the struct has the given key
$assert.key(struct, key, message);

//assert the length of a string, array, structure or query
$assert.lengthOf(object, length, message);
```

### Advanced Expectation Methods
```cfml
//assert value is greater than target
expect(value).toBeGT(target, message);

//assert value is greater than or equal to target
expect(value).toBeGTE(target, message);

//assert value is less than target
expect(value).toBeLT(target, message);

//assert value is less than or equal to target
expect(value).toBeLTE(target, message);

//assert that the needle is included in string or array, not case-sensitive
expect(value).toInclude(needle, message);

//assert that the needle is included in string or array, case-sensitive
expect(value).toIncludeWithCase(needle, message);

//assert value between min and max
expect(value).toBeBetween(min, max, message);

//assert that the value is within +/- a passed delta and optional datepart
expect(value).toBeCloseTo(expected, delta, datePart, message);

//assert value is of CFML type using isValid function.
expect(value).toBeTypeOf(type, message);

//assert value an instance of named object type.
expect(value).toBeInstanceOf(typeName, message);

//assert value to match regex, not case-sensitive.
expect(value).toMatch(regex, message);

//assert function throws exception, optionally specify type or regex.
expect( function(){ x=1/0; } ).toThrow(type, regex, message);

// asset that value is a JSON string.
expect(value).toBeJSON();
```

### Expectation Negation and Chaining
```cfml
expect(5).notToBe(6);

expect(5).notToBe(6).toBeGT(0).toBeLT(10);
```

## SSL/HTTPS Configuration

### Generate SSL Certificate with Keytool
```bash
# Generate private key and keystore
cfroot\jre\bin\keytool -genkeypair -alias certificatekey -keyalg RSA -validity 7 -keystore keystore.jks

# Alternative method
cfroot\jre\bin\keytool -genkey -alias tomcat -keyalg RSA

# Export certificate
cfroot\jre\bin\keytool -export -alias certificatekey -keystore keystore.jks -rfc -file selfsignedcert.cer

# Import certificate to truststore
cfroot\jre\bin\keytool.exe -importcert -keystore "cfroot\jre\lib\security\cacerts" -file selfsignedcert.cer -storepass password
```

### Configure Tomcat SSL Connector (server.xml)
```xml
<Connector port="8443" protocol="HTTP/1.1"
    SSLEnabled="true" maxThreads="150" scheme="https"
    secure="true" keystoreFile="<certificate_location>\.keystore" keystorePass="<password>" keyAlias="tomcat"   clientAuth="false" sslProtocol="TLS" />
```

### Configure Jetty SSL Listener (jetty.xml)
```xml
<Call name="addConnector">
<Arg>
<New class="org.mortbay.jetty.security.SslSocketConnector">
<Set name="Port">8443</Set>
<Set name="maxIdleTime">30000</Set>
<Set name="keystore"><SystemProperty name="jetty.home" default="." />/etc/server.jks</Set>
<Set name="password">changeit</Set>
<Set name="keyPassword">changeit</Set>
<Set name="truststore"><SystemProperty name="jetty.home" default="." />/etc/server.jks</Set>
<Set name="trustPassword">changeit</Set>
</New>
</Arg>
</Call>
```

## Web Server Configuration

### Built-in Tomcat Connector (server.xml)
```xml
<Connector executor="tomcatThreadPool"
    port="8500" protocol="org.apache.coyote.http11.Http11Protocol"
    connectionTimeout="20000"
    redirectPort="8445"/>
```

### Enable Symbolic Links in Tomcat (context.xml)
```xml
<Context allowLinking="true">
```

### Virtual Directory Configuration (server.xml)
```xml
<Context path="/" docBase="<absolute_path_to_cfrootectory>\\wwwroot" WorkDir="       <cf_home>\\runtime\\conf\\Catalina\\localhost\\tmp" aliases="/path1=<absolute_path_to_directory1>,/path2=        <absolute_path_to_directory2>"></Context>
```

### JVM Configuration (jvm.config)
```properties
java.home: [Java home path]
java.args: [JVM arguments, e.g., -Xmx512m]
java.library.path: [Library path settings]
java.class.path: [Additional classpath settings, comma-separated]
```

## Web Server Connectors (wsconfig)

### IIS Configuration
```bash
wsconfig.exe -ws iis -site <site_no>
wsconfig.exe -ws iis -site <site_name>
wsconfig.exe -ws iis -site <site_no> -cluster <cluster-name>
```

### Apache Configuration
```bash
# Windows
wsconfig.exe ws apache dir <apache_conf_directory>
wsconfig.exe ws apache dir <apache_conf_directory> bin <apache_bin_directory>/httpd script <apache_bin_directory>/apachectl
wsconfig.exe -ws apache dir <apache_conf_directory> -cluster <cluster-name>

# Linux/Mac
./wsconfig ws apache dir <apache_conf_directory>
./wsconfig ws apache dir <apache_conf_directory> bin <apache_bin_directory>/httpd script <apache_bin_directory>/apachectl
./wsconfig -ws apache dir <apache_conf_directory> -cluster <cluster-name>
```

### Connector Management
```bash
# Remove connectors
wsconfig.exe -remove -ws iis -site <site_no>
wsconfig.exe -remove iis -site <site_name>
./wsconfig -remove ws apache dir <apache_conf_directory>

# Uninstall and list
./wsconfig -uninstall
./wsconfig -list
```

## Clustering Configuration

### Tomcat Cluster Setup (server.xml)
```xml
<Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster" channelSendOptions="8">
<Manager notifyListenersOnReplication="true" 
expireSessionsOnShutdown="false" className="org.apache.catalina.ha.session.DeltaManager">
</Manager>
<Channel className="org.apache.catalina.tribes.group.GroupChannel">
<Membership port="45565" dropTime="3000" address="228.0.0.4"        className="org.apache.catalina.tribes.membership.McastService" frequency="500">
</Membership>
<Receiver port="4003" autoBind="100" address="auto" selectorTimeout="5000" maxThreads="6" className="org.apache.catalina.tribes.transport.nio.NioReceiver">
</Receiver>
<Sender className="org.apache.catalina.tribes.transport.ReplicationTransmitter">
<Transport className="org.apache.catalina.tribes.transport.nio.PooledParallelSender">
</Transport>
</Sender>
<Interceptor className="org.apache.catalina.tribes.
group.interceptors.TcpFailureDetector">
</Interceptor>
<Interceptor className="org.apache.catalina.tribes.group.
interceptors.MessageDispatch15Interceptor">
</Interceptor>
</Channel>
<Valve className="org.apache.catalina.ha.tcp.ReplicationValve"
filter="">
</Valve>
<Valve className="org.apache.catalina.ha.session.JvmRouteBinderValve">
</Valve>

<ClusterListener className="org.apache.catalina.ha.session.
JvmRouteSessionIDBinderListener">
</ClusterListener>
<ClusterListener className="org.apache.catalina.ha.session.ClusterSessionListener">
</ClusterListener>

</Cluster>
```

## Development Tools

### Running CFDocs Locally
```bash
box server start
```

## Version History

### ColdFusion 4.5 Features
```cfml
<!-- Accessing scopes as structures -->
<cfset myURLParam = url.paramName>
<cfset myFormValue = form.fieldName>
<cfset myCookieValue = cookie.cookieName>

<!-- Java Integration: Creating a Java object -->
<cfset myArrayList = createObject("java", "java.util.ArrayList")>
<cfset myArrayList.add("item1")>

<!-- Java Integration: Using a CFServlet -->
<cfservlet code="my.package.MyServletClass">
```

## Documentation JSON Schema

### Field Reference
```
name: The name of the tag or function, use lowercase.
type: Either `function` or `tag` or `listing`
syntax: The basic syntax of the tag or function
script: For tags, shows how the tag would be invoked from cfscript.
member: For functions, shows the available member function syntax.
returns: The returntype of a function. Valid options are: `any`, `array`, `binary`, `boolean`, `date`, `function`, `guid`, `numeric`, `query`, `string`, `uuid`, `variableName`, `void`, `xml`. Default value is `void`.
related: An array of tag or function names that are related to this item.
description: A short description of the item.
discouraged: If this key exists and has content a warning is displayed stating that the tag or function is discouraged by the CFML community.
params: Array of structures containing information about the attributes of a tag, or arguments of a function.
engines: CFML engine implementation specific info goes here
links: Use this to link to blog entries or other useful related content.
examples: Show example code with expected results.
```

### JSON Structure Example
```json
{
    "name":"nameOfTagOrFunction",
    "type":"function|tag",
    "syntax":"Tag(arg)|<cftag attr=1>",
    "member":"item.memberFunction([args])",
    "script":"cftag(attr=1);",
    "returns":"void",
    "related":[
        "tag",
        "function"
    ],
    "description":"A short description that describes what the tag or function does.",
    "discouraged":"Only add this key if this tag/function is discouraged by the community. Displays a warning.",
    "params":[
        {"name":"funcArgNameOrTagAttributeName", "description":"What it does", "required":true, "default":"false", "type":"boolean", "values":[]}
    ],
    "engines":{
        "coldfusion":{"minimum_version":"10", "notes":"CF Specific Info Here", "docs":"http://learn.adobe.com/wiki/display/coldfusionen/function"},
        "lucee":{"minimum_version":"4.5", "notes":"Lucee Specific Info Here", "docs":"https://docs.lucee.org/reference/functions/name.html"},
        "railo":{"minimum_version":"4.1", "notes":"Railo Specific Here", "docs":"http://railodocs.org/index.cfm/function/sessionrotate"}
    },
    "links":[
        {
            "title":"Title of a blog entry that has good info about this.",
            "description":"Description of the link",
            "url":"http://www.example.com/a/b.cfm"
        }
    ],
    "examples":[
        {
            "title":"Name of the code example",
            "description":"Description of the code example",
            "code":"<cf_examplecodehere>",
            "result":"The expected output of the code example",
            "runnable":true
        }
    ]
}
```

---

*This documentation was generated from the CFDocs project by foundeo, a community-maintained CFML reference tool.*