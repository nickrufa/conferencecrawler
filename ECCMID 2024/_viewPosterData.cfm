<cfprocessingdirective pageEncoding="UTF-8"><!DOCTYPE html>
<cfparam name="thisPageAction" default="display">
<cfparam name="url.thisID" default="">
<cfparam name="url.thissession_title" default="">
<cfparam name="url.thissession_date" default="">
<cfparam name="url.thisabstract_title" default="">
<cfparam name="url.showParsed" default="1">
<cfparam name="pagenum" default="1">

<cfset paginationLimit = 25>
<cfset paginationCacheInterval = 1000>
<cfset recordStart = pagenum * paginationLimit>
<cfset cacheLimit = pagenum * 25>
<cfset cfstart = -int(recordStart/paginationCacheInterval)*1000+recordStart>
<cfif cfstart lt 1>
    <cfset cfstart = 1>
</cfif>


<style>
    .dismissModalPoster {
        display: none;
    }
</style>

<cfquery name="getAllECCMIDPosterData" datasource="#application.dsn#">
    SELECT *
    FROM ECCMID_Posters_2024_03_27
    WHERE 0=0
    ORDER BY id, poster_number, session_title 
</cfquery>
<cfif 0><cfdump var="#getAllECCMIDPosterData#" label="getAllECCMIDPosterData"></cfif>

<cfquery name="getFilteredECCMIDPosterData" dbtype="query">
    SELECT *
    FROM getAllECCMIDPosterData
    WHERE 0=0
    <cfif len(trim(thissession_date))>AND session_date = <cfqueryparam cfsqltype="cf_sql_varchar" value="#thissession_date#"></cfif>
    <cfif len(trim(thissession_title))>AND session_title = <cfqueryparam cfsqltype="cf_sql_varchar" value="#thissession_title#"></cfif>
    ORDER BY id, poster_number, session_title
</cfquery>
<cfif 0><cfdump var="#getFilteredECCMIDPosterData#" label="getFilteredECCMIDPosterData"></cfif>

<cfif isnumeric(trim(url.thisID))>
    <cfquery name="getOneECCMIDPoster" dbtype="query">
        SELECT *
        FROM getAllECCMIDPosterData
        WHERE 0=0
        AND id = <cfqueryparam cfsqltype="cf_sql_integer" value="#url.thisID#">
        ORDER BY id,poster_number, session_title 
    </cfquery>
    <cfif 0><cfdump var="#getOneECCMIDPoster#" label="getOneECCMIDPoster"></cfif>
</cfif>

<cfquery name="getECCMIDDates" dbtype="query">
    SELECT distinct(session_date)
    FROM getAllECCMIDPosterData
</cfquery>
<cfif 0><cfdump var="#getECCMIDDates#" label="getECCMIDDates"></cfif>

<cfquery name="getECCMIDsession_titles" dbtype="query">
    SELECT distinct(session_title) as session_title
    FROM getAllECCMIDPosterData
    WHERE 0=0
</cfquery>
<cfif 0><cfdump var="#getECCMIDsession_titles#" label="getECCMIDsession_titles"></cfif>

<cfquery name="getFilteredECCMIDsession_titles" dbtype="query">
    SELECT distinct(session_title) as session_title
    FROM getFilteredECCMIDPosterData
    WHERE 0=0
</cfquery>
<cfif 0><cfdump var="#getFilteredECCMIDsession_titles#" label="getFilteredECCMIDsession_titles"></cfif>

<html lang="en-US">
    
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title></title>
      <!-- Google Font: Source Sans Pro -->
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
      <!-- Font Awesome -->
      <link rel="stylesheet" href="../../plugins/fontawesome-free/css/all.min.css">
      <!-- DataTables -->
      <link rel="stylesheet" href="../../plugins/datatables-bs4/css/dataTables.bootstrap4.min.css">
      <link rel="stylesheet" href="../../plugins/datatables-responsive/css/responsive.bootstrap4.min.css">
      <link rel="stylesheet" href="../../plugins/datatables-buttons/css/buttons.bootstrap4.min.css">
      <!-- Theme style -->
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.1/dist/css/adminlte.min.css">
    
      
      <meta name="csrf-token" content="XYZ123">
      <style>
        .split {-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;overflow-y: auto;overflow-x: hidden;}
        .gutter {background-color: transparent;background-repeat: no-repeat;background-position: 50%;}
        .gutter.gutter-horizontal {cursor: col-resize;background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAeCAYAAADkftS9AAAAIklEQVQoU2M4c+bMfxAGAgYYmwGrIIiDjrELjpo5aiZeMwF+yNnOs5KSvgAAAABJRU5ErkJggg=='); }
        .gutter.gutter-vertical {cursor: row-resize;background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAFAQMAAABo7865AAAABlBMVEVHcEzMzMzyAv2sAAAAAXRSTlMAQObYZgAAABBJREFUeF5jOAMEEAIEEFwAn3kMwcB6I2AAAAAASUVORK5CYII='); }
        .split.split-horizontal, .gutter.gutter-horizontal { height: 100%;float: left;}
        .navbar-ccms {
          background: linear-gradient(90deg,#dd0452,#d05dab);
        }
        .row > .template_1,
        .row > .template_2 {
          text-align: center;
        }
        .ck-editor__editable_inline {
          min-height: 250px;
        }
        #email_TextAssets:hover {
          border: dashed 2px black;
        }
        .list-group {
          border: dashed 1px blue;
          background-color: gainsboro
        }
        .list-group-none, .list-group-none .list-group-item {
          border: none;
          background: none;
        }
      </style>
    </head>
    <cfset application.dsn = "#application.dsn#">
    <body>  

<div class="container">

    <!--- DATES --->
    <cfoutput>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body bg-light">
                        <div class="text-center my-2">
                            <a class="btn btn-sm btn-outline-secondary<cfif not len(trim(url.thissession_date))> active</cfif>" href="/_viewPosterData.cfm?page=Posters&amp;thissession_title=#url.thissession_title#&amp;thissession_date=">ALL</a>
                            <cfloop query="getECCMIDDates">
                                <a class="btn btn-sm btn-outline-secondary<cfif getECCMIDDates.session_date is '#url.thissession_date#'> active</cfif>" href="/_viewPosterData.cfm?page=Posters&amp;thissession_title=#url.thissession_title#&amp;thissession_date=#session_date#">#session_date#</a> 
                            </cfloop>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </cfoutput>

    <!--- SESSION TITLES --->
    <cfoutput>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body bg-light">
                        <div class="text-left my-2">
                            <ul><li><a class="my-1<cfif not len(trim(getFilteredECCMIDsession_titles.session_title))> active</cfif>" href="/_viewPosterData.cfm?page=Posters&amp;thissession_title=&amp;thissession_date=#thissession_date#">ALL</a></li>
                            <cfloop query="getFilteredECCMIDsession_titles">
                                <li><a class="my-1<cfif getFilteredECCMIDsession_titles.session_title is '#url.thissession_title#'> active</cfif>" href="/_viewPosterData.cfm?page=Posters&amp;thissession_title=#getFilteredECCMIDsession_titles.session_title#&amp;thissession_date=#thissession_date#"><cfif len(trim(getFilteredECCMIDsession_titles.session_title))>#getFilteredECCMIDsession_titles.session_title#<cfelse>Other</cfif></a></li>
                            </cfloop>
                        </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </cfoutput>

    <!--- ABSTRACT TITLES --->
    <div class="row">
        <div class="col-12">
            <div class="card bg-primary">
                <div class="card-body bg-light">
                    <div class="text-center my-2">
                        <!--- cfset breakCounter = 1>
                        <cfoutput query="getFilteredECCMIDPosterData">
                            <cfif find(trim(url.thissession_title), session_title)>
                                <a class="btn btn-sm btn-outline-primary m-2<cfif getFilteredECCMIDPosterData.id is '#url.thisID#'> active</cfif>" href="/_viewPosterData.cfm?page=Posters&amp;thisID=#id#&amp;thisPageAction=view&amp;thissession_title=#url.thissession_title#&amp;thissession_date=#thissession_date#">#poster_number#</a> 
                                <cfif NOT breakCounter mod 5></div><div class="text-center my-2"></cfif>
                                <cfset breakCounter = breakCounter+1>
                            </cfif>
                        </cfoutput --->

                        <table id="fromBinaries" class="table table-sm">
                            <thead>
                                <tr>
                                    <cfoutput><th class="text-center">#rereplace(rereplace(getFilteredECCMIDPosterData.columnlist,',','</th><th>','ALL'),'_',' ','ALL')#</th></cfoutput>
                                </tr>
                            </thead>
                            <tbody class="text-left">
                                <cfoutput query="getFilteredECCMIDPosterData">
                                    <tr>
                                        <td><cfloop list="#columnlist#" index="l">#evaluate(l)#</td><td></cfloop></td>
                                    </tr>
                                </cfoutput>
                            </tbody>   
                        </table>

                    </div>
                </div>
            </div>
        </div>
    </div>

    <cfif isnumeric(trim(url.thisID))>
        <div class="row">
            <div class="col-12 text-center">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <cfoutput><th class="text-center">#rereplace(rereplace(getOneECCMIDPoster.columnlist,',','</th><th>','ALL'),'_',' ','ALL')#</th></cfoutput><th>x</th>
                        </tr>
                    </thead>
                    <tbody class="text-left">
                        <cfoutput query="getOneECCMIDPoster" startrow="1" maxrows="1">
                            <tr>
                                <td>
                                    <cfloop list="#columnlist#" index="l">
                                        #evaluate(l)#</td><td>
                                    </cfloop>
                                </td>
                            </tr>
                        </cfoutput>
                    </tbody>   
                </table>
            </div>
        </div>
    </cfif>

</div>

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
<script src="https://code.jquery.com/ui/1.13.1/jquery-ui.min.js" integrity="sha256-eTyxS0rkjpLEo16uXTS0uVCS4815lc40K2iVpWDvdSY=" crossorigin="anonymous"></script>
      
<!-- Bootstrap 4 -->
<script src="../../plugins/bootstrap/js/bootstrap.bundle.min.js"></script>

<!-- DataTables  & Plugins -->
<script src="../../plugins/datatables/jquery.dataTables.min.js"></script>
<script src="../../plugins/datatables-bs4/js/dataTables.bootstrap4.min.js"></script>
<script src="../../plugins/datatables-responsive/js/dataTables.responsive.min.js"></script>
<script src="../../plugins/datatables-responsive/js/responsive.bootstrap4.min.js"></script>
<script src="../../plugins/datatables-buttons/js/dataTables.buttons.min.js"></script>
<script src="../../plugins/datatables-buttons/js/buttons.bootstrap4.min.js"></script>
<script src="../../plugins/jszip/jszip.min.js"></script>
<script src="../../plugins/pdfmake/pdfmake.min.js"></script>
<script src="../../plugins/pdfmake/vfs_fonts.js"></script>
<script src="../../plugins/datatables-buttons/js/buttons.html5.min.js"></script>
<script src="../../plugins/datatables-buttons/js/buttons.print.min.js"></script>
<script src="../../plugins/datatables-buttons/js/buttons.colVis.min.js"></script>

<script>
  $(function () {
    $("#example1").DataTable({
      "responsive": true, "lengthChange": false, "autoWidth": false,
      "buttons": ["copy", "csv", "excel", "pdf", "print", "colvis"]
    }).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');

    $("#example2").DataTable({
      "responsive": true,
      "lengthChange": false,
      "autoWidth": false
      //"buttons": ["copy", "csv", "excel", "pdf", "print", "colvis"]
    }).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');

    $('#fromBinaries').DataTable({
      "paging": true,
      "lengthChange": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "autoWidth": false,
      "responsive": true,
      "lengthMenu": [ [3, 25, 50, -1], [3, 25, 50, "All"] ],
      "dom": '<"top"lfp>rt<"bottom"i><"clear">'
    });

    $('#fromText').DataTable({
      "paging": true,
      "lengthChange": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "autoWidth": false,
      "responsive": true,
      "lengthMenu": [ [3, 25, 50, -1], [3, 25, 50, "All"] ],
      "dom": '<"top"lfp>rt<"bottom"i><"clear">'
    });

    $('#fromMedia').DataTable({
      "paging": true,
      "lengthChange": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "autoWidth": false,
      "responsive": true,
      "lengthMenu": [ [3, 25, 50, -1], [3, 25, 50, "All"] ],
      "dom": '<"top"lfp>rt<"bottom"i><"clear">'
    });

    $('#fromFragments').DataTable({
      "paging": true,
      "lengthChange": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "autoWidth": false,
      "responsive": true,
      "lengthMenu": [ [3, 25, 50, -1], [3, 25, 50, "All"] ],
      "dom": '<"top"lfpjq>rt<"bottom"i><"clear">'
    });
  });
</script>
</body>
</html>
<cfsetting showdebugoutput="no">