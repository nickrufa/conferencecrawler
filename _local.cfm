<cfscript>

application.cachebuster = rereplace(now(),'\D','','ALL');
application.datasource = 'conference_crawler';
application.dsn  = 'conference_crawler';
application.directory = "/Users/nancyrobasco/workspace/git/conferencecrawler.com/";
application.domain = 'local.dev.conferencecrawler.com';
application.domain_name = 'http://local.dev.conferencecrawler.com';
application.logger_path = "/Users/nancyrobasco/workspace/git/conferencecrawler.com/admin/logs";
application.server = 'local';
application.showdebug = 0;
application.sitename = ' MedTix Conference Crawler';
emailSender = 'webmaster@cmeunited.com';

cfheader(name="Cache-Control", value="no-cache, no-store, must-revalidate");
cfheader(name="Pragma", value="no-cache");
cfheader(name="Expires", value="0");
    /*
    session.userprofileemail = 'nancy@cmeunited.com';
    session.userprofilefirst = 'Nancy';
    session.userprofileid = 8;
    session.userprofilelast = 'Robasco';
    session.userprofilemi = '';
    session.userprofilename = 'Nancy Robasco';
    session.isadmin = 1;
    session.userprofiledepartments = '6';
    session.userprofileroles =  1;
    */
</cfscript>
