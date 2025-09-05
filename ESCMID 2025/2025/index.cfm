<!--- read_posters.cfm - Reads and displays poster data from JSON file --->
<cfscript>
    // Read the JSON file
    try {
        fileContent = fileRead(expandPath("ESCMID-2025-Posters.json"));
        
        // Deserialize the JSON into a ColdFusion data structure
        posterData = deserializeJSON(fileContent);
        
        // Get some stats about the data
        posterCount = arrayLen(posterData);
    }
    catch (any e) {
        errorMessage = "Error processing the file: " & e.message;
    }
</cfscript>

<!DOCTYPE html>
<html>
<head>
    <title>Conference Poster Data</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .stats { background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .error { background-color: #ffdddd; padding: 10px; border-radius: 5px; color: #cc0000; }
    </style>
</head>
<body>
    <h1>Conference Poster Data</h1>
    
    <cfif isDefined("errorMessage")>
        <div class="error">
            <cfoutput>#errorMessage#</cfoutput>
        </div>
    <cfelse>
        <div class="stats">
            <cfoutput>
                <strong>File:</strong> /2025/posters.json<br>
                <strong>Total Posters:</strong> #posterCount#
            </cfoutput>
        </div>
        
        <!--- Dump the data structure for inspection --->
        <h2>Complete Data Structure:</h2>
        <cfdump var="#posterData#" label="Poster Data" expand="false">
        
        <!--- Show the first poster in detail --->
        <cfif posterCount gt 0>
            <h2>First Poster Details:</h2>
            <cfdump var="#posterData[1]#" label="First Poster" expand="true">
        </cfif>
    </cfif>
</body>
</html>