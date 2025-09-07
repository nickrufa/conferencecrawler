# Background
## Purpose and Crawl Process

Each year these large medical congressess have live sessions and poster presentations, held in cities across the globe. they publish the details/schedule through 3rd-party meeting websites, like eventscribe, or key4.live.

Biotech companies will send their MSLs to these meetings to discover new information important for their industry. They must divide the session and poster analysis among the team members, ahead of the meetings, to select and rank the ones important to them. Typically this ends up in a multi-tab excel file.

While each website is different, they generally will post a page with all session/poster CATEGORIES, TITLES, IDs (sometimes nested under a date or the category), and further, each individual session/poster will have an AJAX call to a modal window, with additional details we must capture for each row of the session/poster list.

In the past, I manually crawled the session and poster lists, saved locally, parsed the IDs, then scripted a simple crawler to capture the details from the AJAX, then saved to a mysql table for additional manipulation, finally ending up in excel for the MSL teams.

I have done initial crawls and saved the lists of posters and sessions to @IDWEEK2025/IDWeek2025 posters.txt and @IDWEEK2025/IDWeek2025 symposia.txt . I use the IDs to crawl the URLS shown in the modals. For IDWEEK2025, which is the next meeting, for posters, I would crawl `https://idweek2025.eventscribe.net/fsPopup.asp?PosterID=760991&mode=posterInfo` and save each HTML response to mysql table `IDWEEK_Posters_2025`

Similarly for sessions, we look for a `data-presid`, then the `data-url` and within that, we also want the start/end times for any sub-sessions and the faculty role/details. Note that we don't care about website media, images, etc.

Session link:
`https://idweek2025.eventscribe.net/ajaxcalls/SessionInfo.asp?PresentationID=1607469`

One or more: Sub-session links:
`https://idweek2025.eventscribe.net/ajaxcalls/PresentationInfo.asp?PresentationID=1607477&returl=YWpheGNhbGxzL3Nlc3Npb25pbmZvLmFzcD9QcmVzZW50YXRpb25JRD0xNjA3NDY5`

The goal is to use LLM/AI to optimize the crawl, data extraction, and provide the detail the MSLs need, in the best way possible for them to view the data, make sense of it, and schedule their congress days. We can start with existing output, such as Excel, but open to more interactive methods, such as PWA on mobile devices, with offline, access so their can have data at the ready.

Let's create a plan that handles 1) crawl, 2) export, and 3) enhanced tool.
