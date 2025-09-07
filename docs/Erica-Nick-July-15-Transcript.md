# Conversation Summary: Conference Coverage Process Between Erica Fernandez and Nicholas Rufa

This document summarizes and cleans up a video transcript from a discussion on July 15 (based on filename) between Erica Fernandez (Medical Affairs team) and Nicholas Rufa (Nick, likely in a technical or development role). The conversation focuses on the current manual processes for conference coverage (e.g., SMID, ID Week), use of Excel for tracking sessions and posters, integration with AI tools like Copilot for analysis, and ideas for a more automated platform. The transcript has been edited for clarity, removing fillers (e.g., "um," "yeah"), repetitions, and timestamps while preserving the original meaning and flow.

The discussion highlights inefficiencies in Field Medical teams' workflows, such as manual data entry, downloading posters, and post-conference analysis. Key pain points and needs are called out in dedicated sections at the end.

## Cleaned Transcript

**Erica:** I can run back and ask Copilot, "Can you go through again what we talked about with XYZ?" I was doing that for this debrief meeting before our call. With Journal Watch, this data is important for awareness—it's out there in the ether—but it's not a big deal for "In Your Bag." Instead, it could be useful for Journal Watch.

**Nick:** Awesome.

**Erica:** Anything for "In Your Bag" post-approval or Journal Watch must be original research—not from symposia. It could be an oral abstract, e-flash poster, poster presentation, or session presenting study findings. Symposia are more like lectures combining different topics.

For ESMID in particular—and I'll check the ID Week website, as it's being updated—the symposia, oral abstracts, and posters have slightly different names than at ESMID, but the idea is the same. If it's original data, we consider it for "In Your Bag" or Journal Watch. For posters or slides, you need permission to use them.

That's why we have those three columns on the symposia Excel sheet—they included oral abstracts. We kept them separated as on the website: one for symposia with oral abstracts, and posters separately.

Let me switch to the poster sheet to show you—it's similar but a different color. It has the strategic objectives, "In Your Bag" columns, etc. One difference: with posters, we can download PDFs; with ESMID, we used shortcut keys because they don't allow it easily.

We need a standard naming method for PDFs. I created hidden columns with a formula combining poster number and abstract number. They'd copy-paste the name when printing/saving.

In an app, you could upload the poster, and the name would auto-generate based on a standard. At the end, for Journal Watch recommendations, you could filter by drug (e.g., Ridvansin), review them quickly, approve/reject, and download agreed-upon posters.

**Nick:** So, at the poster, there's a QR code or download option right there?

**Erica:** They do it on the website, so I might download before arriving. Poster titles are available 2 weeks in advance, but the full poster isn't. I might assign a title to myself if relevant, then review the full poster later and mark as not relevant if needed.

I go back and forth on auto-downloading posters into the app once available—so I can just click, review, and mark relevance without downloading manually. But that could be complex depending on the conference. ESMID is almost impossible; we used shortcut keys and got PNGs—it was a mess.

This is the super-manual way with Excel.

Our old output drove me insane—data-heavy slides from conference lunch-and-learns, boring everyone in clinical development or EC. This year, we shifted to a 30,000-foot view, focusing on insights and common themes, comparing them to CRM insight analysis and social listening for a holistic ecosystem view.

**Nick:** Yeah.

**Erica:** Our output is manual—I don't expect a platform to generate the PowerPoint. Let me show the final output we presented to the EC, but more importantly, the intermediate steps that Medical gets.

We focused on high-level insights per drug. Basic analysis from Excel (e.g., total posters/sessions at ESMID, how many MSD reviewed, how many relevant) could use pivot tables— a platform should pull these numbers easily.

**Nick:** Right, these are usage stats and reporting on what was done.

**Erica:** Exactly. For insights, we combined conference data (using icons for conference, MSD interactions, social listening). Social comes from our platform; MSD interactions from Steve Rock/CRM. Meeting insights from the Excel.

To get here, I created a final database combining all posters/oral sessions into one Excel with MSD notes and insights. I unified columns, then created a VLOOKUP sheet: enter session code, and it pulls title, author, MSD notes, insights.

Someone requested more fields for lookup, but I don't have time—I'm not an Excel wizard.

They use this with the final written report, separated by product (e.g., Resafungen, Marafenamaberbactam). I separated to avoid overwhelming Copilot; focused prompts like "only answer from this."

I created Copilot agents describing columns, focusing on insights but using title/MSD notes for context.

For each drug, the report format: key themes regarding the drug, key insights on disease states, summaries of original research.

Example with Mirapet and Maverbaktam: top categories of insights by disease state (e.g., CUTI, CNS infections), competitive landscape. Always reference sources (session/poster number) so users can check the database for full context.

For original research, summaries include title, code, covering team member, MSD notes, insights—easier than raw Excel. I reviewed these to ensure nothing was missed.

Sections varied by drug/content. We included MSD interactions from AI Analytics/CRM and social media from OLA runs (sometimes minimal).

The report organizes Excel data, highlights recurring themes, for deciding slide content.

Back to Excel: for categories like competitors (e.g., Dalvavancin as competitor to Oridavancin), we tag "competitor" in topic. This allowed filtering for key takeaways on competitors.

Same for pipeline competitors.

**Nick:** Yeah.

**Erica:** That's it—I think I've been rambling.

**Nick:** It's very good. I hadn't seen how it gets used after. Seeing the final PowerPoint to EC, your AI work, and how you kept sources is awesome.

**Erica:** For ID Week, we still want to scrape the site. From your perspective, if this is high priority to develop, do you think other teams would be interested?

**Nick:** I think so. Pain points are probably shared. Bigger companies might use tools, but I don't know. Novo isn't—my husband is an MSL there and hates color-coding Excels.

**Nick:** It's worthwhile. We're doing the first 20% already (setup). You do the hard work at the meeting and post-crunch. Real-time insights/tagging collaboratively would help—combine without separate Excel work later.

**Erica:** Any real-time dashboarding: daily reports to commercial (e.g., sessions/posters attended). Option for quick notes/overheard insights—Sandy can share daily "quickies" from MSDs, showing Medical's value.

Marvelous (but not necessary): integrate KOL conversations at conference into the platform, capture insights holistically, forward to CRM (e.g., Viva via Tika MSL). Reduces double-entry (platform + Steve Rock), lets MSLs focus on analysis.

Makes post-meeting decisions faster (e.g., Q4 targets), less November burnout.

**Nick:** Yeah.

**Erica:** I'll send the database, final report, and my team presentation on changes (with/without platform).

**Nick:** I'd love to see it. Way back, reports in old systems like Perceptum went over my head—walking through it now is different.

**Erica:** The real value: analyze insights to inform strategy real-time at congress. Some pay thousands to hire coverage teams—I wonder how useful if not subject matter experts. Better to send own MSLs with platform pulling value.

**Nick:** Agree—hired teams lack deep knowledge unless experienced in ID.

**Erica:** One more: Christine asks at EC meetings, "What was the most interesting thing you heard?" A field for that, reportable daily, proves value to EC—get more money.

**Nick:** Right.

**Erica:** That's it. Thanks—I'll send the info.

**Nick:** Thanks, Erica—this was great. I'll look for Copilot stuff; if not, I'll reach out. I'll check on Steve Rock cases.

## Key Pain Points of Field Medical Teams

- **Manual Data Management in Excel:** Heavy reliance on Excel for tracking sessions, posters, and insights—requires manual entry, hidden columns, formulas, pivot tables, and VLOOKUPs. Time-consuming and error-prone; Erica describes herself as "not an Excel wizard."
- **Downloading and Naming Files:** Inconsistent poster/PDF naming; manual downloads (e.g., shortcut keys for ESMID, PNG messes). Pre-conference availability varies, leading to back-and-forth reviews.
- **Permission and Separation of Content:** Need to track permissions for posters/slides; separating symposia, oral abstracts, and posters manually.
- **Post-Conference Analysis Overload:** Combining data from multiple sheets/sources; manual insight summarization. Old outputs were "data-heavy" and ineffective for audiences like EC.
- **Double-Entry and Integration Issues:** Entering KOL interactions into platform then CRM (e.g., Steve Rock/Viva)—redundant work. Slows analysis and strategy (e.g., November burnout for Q4 planning).
- **Lack of Real-Time Collaboration and Reporting:** No collaborative tagging/insights during conference; no daily dashboards/stats to show impact (e.g., sessions attended, quick insights) to commercial/EC.
- **Scalability Across Conferences:** Variations (e.g., ESMID vs. ID Week) make automation complex; scraping sites needed but manual.
- **Proving Value to Leadership:** Struggle to demonstrate Medical's impact (e.g., daily reports, "most interesting thing" for EC)—affects budget requests.

## Needs to Be Addressed (Proposed Improvements)

- **Automated Platform/App:** Standardize naming/uploads; auto-download posters if available; filter/review by drug for quick approvals (e.g., Journal Watch).
- **Real-Time Features:** Collaborative tagging/insights; daily dashboards/reports (e.g., sessions attended, quick notes/overheard insights).
- **AI Integration:** Like Copilot, but built-in: generate summaries, key themes, competitive landscapes with source references. Pull stats (e.g., reviewed/relevant items).
- **CRM/KOL Integration:** Capture KOL interactions at conference; auto-forward to CRM to eliminate double-entry.
- **Search and Lookup Enhancements:** Easy VLOOKUP-like functionality with more fields; filter by categories/topics (e.g., competitors, pipeline).
- **Holistic Ecosystem View:** Combine conference insights with CRM/social listening for 30,000-foot analysis.
- **Daily EC Reporting:** Field for "most interesting thing"; automated reports to prove value and inform strategy real-time.
- **Broader Applicability:** Develop for other teams/companies; prioritize based on shared pain points (e.g., Novo's MSLs hate manual Excel color-coding).