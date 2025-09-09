#!/usr/bin/env python3
"""
IDWeek 2025 Faculty HTML Parser
Extracts structured data from faculty presenter HTML stored in raw_data field
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FacultyHTMLParser:
    """Parser for IDWeek 2025 faculty HTML data"""
    
    def __init__(self):
        self.date_patterns = [
            r'(\w+),\s+(\w+)\s+(\d+),\s+(\d+)',  # Tuesday, October 21, 2025
            r'(\w+)\s+(\d+),\s+(\d+)',           # October 21, 2025
            r'(\d+)/(\d+)/(\d+)',                # 10/21/2025
        ]
        
        self.time_pattern = r'(\d+):(\d+)\s+(AM|PM)\s*(?:-\s*(\d+):(\d+)\s+(AM|PM))?\s*(?:<small>(.+?)</small>)?'
    
    def parse_faculty_data(self, raw_html: str, faculty_id: int = None) -> Dict:
        """
        Parse faculty HTML data and extract structured information
        
        Args:
            raw_html: Raw HTML string from database
            faculty_id: Optional faculty ID for logging
            
        Returns:
            Dictionary with parsed faculty data
        """
        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Extract basic faculty info
            faculty_data = self._extract_faculty_info(soup)
            
            # Extract poster information
            posters = self._extract_poster_info(soup)
            
            result = {
                'faculty': faculty_data,
                'posters': posters,
                'parsing_status': 'parsed',
                'parse_error': None
            }
            
            logger.info(f"Successfully parsed faculty {faculty_id}: {faculty_data.get('full_name', 'Unknown')}")
            return result
            
        except Exception as e:
            error_msg = f"Error parsing faculty {faculty_id}: {str(e)}"
            logger.error(error_msg)
            return {
                'faculty': {},
                'posters': [],
                'parsing_status': 'error',
                'parse_error': error_msg
            }
    
    def _extract_faculty_info(self, soup: BeautifulSoup) -> Dict:
        """Extract faculty personal information"""
        faculty_info = {}
        
        # Full name and credentials
        name_elem = soup.find('h1', class_='popupFullName')
        if name_elem:
            full_name = name_elem.get_text(strip=True)
            faculty_info['full_name'] = full_name
            
            # Try to separate name and credentials
            name_parts = self._parse_name_and_credentials(full_name)
            faculty_info.update(name_parts)
        
        # Organization and job title
        org_elem = soup.find('p', class_='popupOrganization')
        if org_elem:
            org_text = org_elem.get_text(strip=True)
            job_title, organization = self._parse_organization_info(org_text)
            faculty_info['job_title'] = job_title
            faculty_info['organization'] = organization
        
        # Photo URL
        photo_elem = soup.find('img', class_='presenterphoto')
        if photo_elem:
            faculty_info['photo_url'] = photo_elem.get('src')
        
        # Email address (from mailto links)
        email_link = soup.find('a', href=re.compile(r'^mailto:'))
        if email_link:
            email_match = re.search(r'mailto:([^"]+)', email_link.get('href', ''))
            if email_match:
                faculty_info['email'] = email_match.group(1)
        
        # Disclosure information
        disclosure_elem = soup.find('p', string=re.compile(r'Disclosure'))
        if not disclosure_elem:
            # Look for text containing "Disclosure"
            for p in soup.find_all('p'):
                if p.get_text() and 'Disclosure' in p.get_text():
                    disclosure_elem = p
                    break
        
        if disclosure_elem:
            faculty_info['disclosure_info'] = disclosure_elem.get_text(strip=True)
        
        # Biography (usually the longest paragraph without specific classes)
        bio_elem = self._find_biography(soup)
        if bio_elem:
            faculty_info['biography'] = bio_elem.get_text(strip=True)
        
        return faculty_info
    
    def _parse_name_and_credentials(self, full_name: str) -> Dict:
        """Parse name and credentials from full name string"""
        # Common credential patterns
        credential_pattern = r',\s*((?:[A-Z]{2,5}(?:\.|,)?(?:\s*)?)+)$'
        match = re.search(credential_pattern, full_name)
        
        if match:
            credentials = match.group(1).strip()
            name = full_name[:match.start()].strip()
            return {'name': name, 'credentials': credentials}
        else:
            return {'name': full_name, 'credentials': None}
    
    def _parse_organization_info(self, org_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse job title and organization from organization text"""
        # Split by <br/> or newlines
        lines = re.split(r'<br/?>', org_text, flags=re.IGNORECASE)
        lines = [line.strip() for line in lines if line.strip()]
        
        if len(lines) >= 2:
            return lines[0], lines[1]  # job_title, organization
        elif len(lines) == 1:
            return None, lines[0]     # only organization
        else:
            return None, None
    
    def _find_biography(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the biography paragraph (usually the longest one)"""
        paragraphs = soup.find_all('p')
        
        # Filter out known non-bio paragraphs
        bio_candidates = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if not text:
                continue
            
            # Skip known non-bio content
            if any(keyword in text for keyword in [
                'Disclosure', 'popupOrganization', 'text-muted', 
                'Copyright', 'Designed by'
            ]):
                continue
            
            # Skip if it has specific classes that indicate non-bio content
            if p.get('class') and any(cls in ['text-muted', 'copyrights'] for cls in p.get('class')):
                continue
            
            bio_candidates.append((p, len(text)))
        
        # Return the longest paragraph as biography
        if bio_candidates:
            bio_candidates.sort(key=lambda x: x[1], reverse=True)
            return bio_candidates[0][0]
        
        return None
    
    def _extract_poster_info(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract poster information from HTML"""
        posters = []
        
        # Find poster links
        poster_links = soup.find_all('a', href=re.compile(r'PosterID=(\d+)'))
        
        for link in poster_links:
            poster_info = {}
            
            # Extract poster ID
            href = link.get('href', '')
            poster_id_match = re.search(r'PosterID=(\d+)', href)
            if poster_id_match:
                poster_info['poster_id'] = poster_id_match.group(1)
                poster_info['url_reference'] = href
            
            # Extract poster title and number
            title_text = link.get_text(strip=True)
            poster_number, title = self._parse_poster_title(title_text)
            poster_info['poster_number'] = poster_number
            poster_info['title'] = title
            
            # Find the parent container for date/time info
            poster_container = link.find_parent('li') or link.find_parent('div')
            if poster_container:
                date_time_info = self._extract_date_time(poster_container)
                poster_info.update(date_time_info)
            
            posters.append(poster_info)
        
        return posters
    
    def _parse_poster_title(self, title_text: str) -> Tuple[Optional[str], str]:
        """Parse poster number and title from title text"""
        # Pattern for poster numbers like (P-1469)
        number_pattern = r'^\(([^)]+)\)\s*(.+)$'
        match = re.match(number_pattern, title_text)
        
        if match:
            return match.group(1), match.group(2).strip()
        else:
            return None, title_text
    
    def _extract_date_time(self, container: Tag) -> Dict:
        """Extract date and time information from poster container"""
        date_time_info = {}
        
        # Look for calendar icon and date
        date_elem = container.find('i', class_='fa-calendar')
        if date_elem:
            date_parent = date_elem.find_parent()
            if date_parent:
                date_text = date_parent.get_text(strip=True)
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    date_time_info['presentation_date'] = parsed_date
        
        # Look for clock icon and time
        time_elem = container.find('i', class_='fa-clock-o')
        if time_elem:
            time_parent = time_elem.find_parent()
            if time_parent:
                time_text = time_parent.get_text(strip=True)
                time_info = self._parse_time(time_text)
                date_time_info.update(time_info)
        
        return date_time_info
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parse date from various formats"""
        # Remove extra whitespace and common prefixes
        date_text = re.sub(r'^.*?(\w+day,?\s+)', r'\1', date_text, flags=re.IGNORECASE)
        
        # Try different date patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 4:  # Tuesday, October 21, 2025
                        month_name = match.group(2)
                        day = int(match.group(3))
                        year = int(match.group(4))
                    elif len(match.groups()) == 3:  # October 21, 2025 or 10/21/2025
                        if match.group(1).isdigit():  # 10/21/2025
                            month = int(match.group(1))
                            day = int(match.group(2))
                            year = int(match.group(3))
                            return f"{year:04d}-{month:02d}-{day:02d}"
                        else:  # October 21, 2025
                            month_name = match.group(1)
                            day = int(match.group(2))
                            year = int(match.group(3))
                    
                    # Convert month name to number
                    if 'month_name' in locals():
                        month_map = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }
                        month = month_map.get(month_name.lower())
                        if month:
                            return f"{year:04d}-{month:02d}-{day:02d}"
                
                except (ValueError, KeyError):
                    continue
        
        return None
    
    def _parse_time(self, time_text: str) -> Dict:
        """Parse time information"""
        time_info = {}
        
        match = re.search(self.time_pattern, time_text)
        if match:
            start_hour = int(match.group(1))
            start_min = int(match.group(2))
            start_ampm = match.group(3)
            
            # Convert to 24-hour format
            if start_ampm.upper() == 'PM' and start_hour != 12:
                start_hour += 12
            elif start_ampm.upper() == 'AM' and start_hour == 12:
                start_hour = 0
            
            start_time = f"{start_hour:02d}:{start_min:02d}"
            
            # Check for end time
            if match.group(4):  # End time exists
                end_hour = int(match.group(4))
                end_min = int(match.group(5))
                end_ampm = match.group(6)
                
                if end_ampm.upper() == 'PM' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.upper() == 'AM' and end_hour == 12:
                    end_hour = 0
                
                end_time = f"{end_hour:02d}:{end_min:02d}"
                time_info['presentation_time'] = f"{start_time} - {end_time}"
            else:
                time_info['presentation_time'] = start_time
            
            # Extract timezone if present
            if match.group(7):
                time_info['time_zone'] = match.group(7).strip()
        
        return time_info


# Test function
def test_parser():
    """Test the parser with sample data"""
    sample_html = '''<div class="popup_content popupmodeside">
        <h1 class="popupFullName mar-no">David Singer, PharmD, MS</h1>
        <p class="text-muted mar-top popupOrganization">Director, US Health Economics and Outcomes Research<br/>GSK</p>
        <p class="text-muted">Disclosure(s): GSK: Employed by GSK, Stocks/Bonds (Public Company)</p>
        <p>David Singer, PharmD, MS, is Director, US Health Economics...</p>
        <ul class="list-view list-group list-unstyled">
            <li class="pad-btm">
                <div class="bold" data-url="/ajaxcalls/PosterInfo.asp?PosterID=759828">
                    <a class="loadbyurl" href="/ajaxcalls/PosterInfo.asp?PosterID=759828">(P-1469) RSV-Related Knowledge, Attitudes, and Practices Among US Adults During the 2024–2025 RSV Season</a>
                </div>
                <div class="clearfix text-muted">
                    <div class="pull-left pres-tidbit tipsytip" title="">
                        <i class="fa fa-calendar fa-fw"></i>Tuesday, October 21, 2025
                    </div>
                    <div class='pull-left pres-tidbit tipsytip' title=''>
                        <i class="fa fa-clock-o fa-fw"></i>12:15 PM - 1:30 PM <small>US ET</small>
                    </div>
                </div>
            </li>
        </ul>
    </div>'''
    
    parser = FacultyHTMLParser()
    result = parser.parse_faculty_data(sample_html, faculty_id=999)
    
    print("Test Results:")
    print("Faculty Data:", result['faculty'])
    print("Posters:", result['posters'])
    print("Status:", result['parsing_status'])


if __name__ == "__main__":
    test_parser()