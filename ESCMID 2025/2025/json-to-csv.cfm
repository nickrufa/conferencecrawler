<!--- posters_json_to_csv.cfm - Converts poster JSON data to CSV format --->

<!--- Set default URL parameters --->
<cfparam name="url.bom" default="true" type="boolean">

<cfscript>
    // Configuration
    jsonFilePath = expandPath("ESCMID-2025-Posters.json");
    csvFilePath = expandPath("ESCMID-2025-Posters.csv");
    
    // Add BOM (Byte Order Mark) to help Excel recognize UTF-8
    // This is important for international characters
    addBOM = url.bom;
    
    // Co-authors delimiter (change this to your preferred character)
    // pipe (|) = chr(124)
    // semicolon (;) = chr(59)
    // line feed (LF) = chr(10)
    // carriage return (CR) = chr(13)
    // CR+LF = chr(13) & chr(10)
    coAuthorsDelimiter = chr(124); // Pipe symbol by default
    
    // Initialize variables
    conversionSuccessful = false;
    message = "";
    detail = "";
    fieldNames = [];
    
    // Read and parse the JSON file
    try {
        fileContent = fileRead(jsonFilePath);
        posters = deserializeJSON(fileContent);
        
        // Find all possible fields across all posters
        fieldSet = {};
        
        // First pass: determine all fields
        for (poster in posters) {
            // Track all regular fields
            for (key in poster) {
                if (key != "co_authors") {
                    fieldSet[key] = true;
                }
            }
        }
        
        // Create ordered list of fieldnames
        fieldNames = structKeyArray(fieldSet);
        arraySort(fieldNames, "textnocase");
        
        // Add a single co-authors column
        arrayAppend(fieldNames, "co_authors");
        
        // Create the CSV content
        csvContent = arrayToList(fieldNames) & chr(13) & chr(10);
        
        // Second pass: create data rows
        for (poster in posters) {
            rowValues = [];
            
            // Add values for each field
            for (field in fieldNames) {
                if (field == "co_authors") {
                    // Handle co-authors as a single cell with specified delimiter
                    if (structKeyExists(poster, "co_authors") && isArray(poster.co_authors) && arrayLen(poster.co_authors) > 0) {
                        // Use the configured delimiter for co-authors
                        
                        // Quote and escape each author individually
                        quotedAuthors = [];
                        for (author in poster.co_authors) {
                            arrayAppend(quotedAuthors, replace(author, '"', '""', "all"));
                        }
                        
                        // Join all quoted authors with the delimiter
                        allAuthors = arrayToList(quotedAuthors, coAuthorsDelimiter);
                        
                        // Quote the entire string again for CSV format
                        arrayAppend(rowValues, '"' & allAuthors & '"');
                    } else {
                        arrayAppend(rowValues, '');
                    }
                } else if (structKeyExists(poster, field)) {
                    // Regular field
                    if (isSimpleValue(poster[field])) {
                        // Quote and escape the value
                        arrayAppend(rowValues, '"' & replace(poster[field], '"', '""', "all") & '"');
                    } else {
                        // Handle non-simple values (shouldn't normally happen)
                        arrayAppend(rowValues, '');
                    }
                } else {
                    // Field doesn't exist in this poster
                    arrayAppend(rowValues, '');
                }
            }
            
            // Add the row to the CSV content
            csvContent &= arrayToList(rowValues) & chr(13) & chr(10);
        }
        
        // Write the CSV file
        // If BOM is enabled, add the UTF-8 BOM (0xEF,0xBB,0xBF) at the beginning of the file
        // This helps Excel correctly interpret UTF-8 encoded text
        if (addBOM) {
            // Create a BOM string (UTF-8 Byte Order Mark)
            bomString = chr(239) & chr(187) & chr(191);
            fileWrite(csvFilePath, bomString & csvContent);
        } else {
            fileWrite(csvFilePath, csvContent);
        }
        
        conversionSuccessful = true;
        message = "Successfully converted #arrayLen(posters)# posters to CSV format";
    }
    catch (any e) {
        conversionSuccessful = false;
        message = "Error: " & e.message;
        detail = e.detail;
    }
</cfscript>

<!DOCTYPE html>
<html>
<head>
    <title>JSON to CSV Conversion</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; margin-bottom: 25px; }
        .success { background-color: #dff0d8; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #3c763d; }
        .error { background-color: #f2dede; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #a94442; }
        .details { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .form-container { margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>JSON to CSV Conversion</h1>
        
        <cfif conversionSuccessful>
            <div class="success">
                <cfoutput>#message#</cfoutput>
            </div>
            
            <div class="details">
                <cfoutput>
                    <p><strong>Source:</strong> #jsonFilePath#</p>
                    <p><strong>Output:</strong> #csvFilePath#</p>
                    <p><strong>Fields:</strong> #arrayLen(fieldNames)# columns</p>
                    <p><strong>Character Encoding:</strong> UTF-8 <cfif addBOM>with BOM (helps Excel read special characters correctly)</cfif></p>
                    <p><strong>Co-authors delimiter:</strong> 
                       <cfif coAuthorsDelimiter EQ chr(124)>Pipe symbol (|)
                       <cfelseif coAuthorsDelimiter EQ chr(59)>Semicolon (;)
                       <cfelseif coAuthorsDelimiter EQ chr(10)>Line feed (LF)
                       <cfelseif coAuthorsDelimiter EQ chr(13)>Carriage return (CR)
                       <cfelseif coAuthorsDelimiter EQ chr(13) & chr(10)>CR+LF
                       <cfelse>ASCII #asc(coAuthorsDelimiter)#
                       </cfif>
                    </p>
                    <ul>
                        <cfloop array="#fieldNames#" index="field">
                            <li>#field#</li>
                        </cfloop>
                    </ul>
                </cfoutput>
            </div>
            
            <p>
                <a href="<cfoutput>#replace(csvFilePath, expandPath('/'), '/')#</cfoutput>" class="btn btn-success" target="_blank">Download CSV file</a>
                
                <!--- Generate links for different export options --->
                <a href="?bom=<cfoutput>#!addBOM#</cfoutput>" class="btn btn-outline-primary ms-2">
                    Switch to CSV <cfoutput>#addBOM ? "without" : "with"#</cfoutput> BOM
                </a>
            </p>
            
            <div class="alert alert-info mt-4">
                <h5>Troubleshooting Character Encoding Issues</h5>
                <p>If you're seeing garbled characters (like "√ñznur G√úNES" instead of "Öznur GÜNES"):</p>
                <ul>
                    <li>Try the "with BOM" option - this helps Excel recognize UTF-8 encoding</li>
                    <li>When opening in Excel, use Data → From Text/CSV and select "UTF-8" encoding</li>
                    <li>For other applications, ensure they're set to read UTF-8 encoded files</li>
                </ul>
            </div>
        <cfelse>
            <div class="error">
                <cfoutput>#message#</cfoutput>
                <cfif len(detail) GT 0>
                    <p>Details: #detail#</p>
                </cfif>
            </div>
            
            <p>
                <a href="posters_json_to_csv.cfm" class="btn btn-primary">Try Again</a>
            </p>
        </cfif>
    </div>
</body>
</html>