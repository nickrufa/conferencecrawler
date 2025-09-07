#!/usr/bin/env python3
"""
IDWeek 2025 Session HTML Parser - Fixed Version
Based on actual HTML structure from sessions
"""

from lxml import html
import re
from typing import Dict, List, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SessionHTMLParserFixed:
    """Fixed parser for IDWeek 2025 session HTML content"""
    
    def __init__(self):
        self.parsed_count = 0
        self.error_count = 0
    
    def parse_session_html(self, html_content: str) -> Dict[str, Any]:
        """Parse session HTML and extract all data"""
        try:
            tree = html.fromstring(html_content)
            
            session_data = {
                'tracks': self._extract_tracks(tree),
                'session_info': self._extract_session_info(tree),
                'schedule': self._extract_schedule_info(tree),
                'credits': self._extract_credit_info(tree),
                'speakers': self._extract_speakers(tree),
                'disclosures': self._extract_disclosures(tree),
                'presentations': self._extract_presentations(tree),
                'raw_html': html_content
            }
            
            self.parsed_count += 1
            title = session_data.get('session_info', {}).get('title', 'Unknown')
            logger.info(f"Successfully parsed session: {title}")
            
            return session_data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error parsing session HTML: {str(e)}")
            return {
                'error': str(e),
                'raw_html': html_content
            }
    
    def _extract_tracks(self, tree) -> Dict[str, Any]:
        """Extract track information - sessions have multiple tracks"""
        try:
            # Tracks are in p.trackname elements
            track_elements = tree.xpath('//p[contains(@class, "trackname")]/text()')
            tracks = [track.strip() for track in track_elements if track.strip()]
            
            return {
                'all_tracks': tracks,
                'primary_track': tracks[0] if tracks else '',
                'track_count': len(tracks)
            }
        except Exception as e:
            logger.warning(f"Error extracting tracks: {e}")
            return {'all_tracks': [], 'primary_track': '', 'track_count': 0}
    
    def _extract_session_info(self, tree) -> Dict[str, str]:
        """Extract basic session information"""
        try:
            # Session type from div containing "Session Type:"
            session_type = ""
            type_divs = tree.xpath('//div[contains(text(), "Session Type:")]/text()')
            if type_divs:
                session_type = type_divs[0].replace("Session Type: ", "").strip()
            
            # Session title from h1
            title_elements = tree.xpath('//h1/text()')
            full_title = title_elements[0].strip() if title_elements else ""
            
            # Parse session number and clean title
            session_number = ""
            clean_title = full_title
            if full_title:
                match = re.match(r'^(\\d+)\\s*-\\s*(.+)', full_title)
                if match:
                    session_number = match.group(1)
                    clean_title = match.group(2).strip()
            
            return {
                'type': session_type,
                'number': session_number,
                'title': clean_title,
                'full_title': full_title
            }
        except Exception as e:
            logger.warning(f"Error extracting session info: {e}")
            return {'type': '', 'number': '', 'title': '', 'full_title': ''}
    
    def _extract_schedule_info(self, tree) -> Dict[str, str]:
        """Extract schedule information"""
        try:
            # Date after fa-calendar icon
            date_elements = tree.xpath('//i[contains(@class, "fa-calendar")]/following-sibling::text()[1]')
            date = date_elements[0].strip() if date_elements else ""
            
            # Time from span with tipsytip class after fa-clock-o
            time_elements = tree.xpath('//i[contains(@class, "fa-clock-o")]/following-sibling::span[@class="tipsytip"]/text()')
            time_raw = time_elements[0].strip() if time_elements else ""
            
            # Parse time and timezone
            time = time_raw
            timezone = ""
            if time_raw:
                # Remove <small>US ET</small> part
                time_match = re.search(r'^([^<]+)', time_raw)
                if time_match:
                    time = time_match.group(1).strip()
                if "US ET" in time_raw:
                    timezone = "US ET"
            
            # Location after fa-map-marker
            location_elements = tree.xpath('//i[contains(@class, "fa-map-marker")]/following-sibling::text()[1]')
            location_raw = location_elements[0].strip() if location_elements else ""
            location = location_raw.replace("Location: ", "").strip()
            
            return {
                'date': date,
                'time': time,
                'timezone': timezone,
                'location': location
            }
        except Exception as e:
            logger.warning(f"Error extracting schedule: {e}")
            return {'date': '', 'time': '', 'timezone': '', 'location': ''}
    
    def _extract_credit_info(self, tree) -> Dict[str, str]:
        """Extract CME credit information"""
        try:
            # Credits in div.mar-top
            credit_elements = tree.xpath('//div[@class="mar-top"]')
            if not credit_elements:
                return {}
            
            credit_text = credit_elements[0].text_content()
            credits = {}
            
            # Extract credit hours using simple patterns
            patterns = {
                'cme_hours': r'CME Credits: Maximum of (\\d+(?:\\.\\d+)?) hours',
                'moc_hours': r'MOC Credits: Maximum of (\\d+(?:\\.\\d+)?) hours', 
                'cne_hours': r'CNE Credits: Maximum of (\\d+(?:\\.\\d+)?) hours',
                'acpe_hours': r'ACPE Credits: ACPE (\\d+(?:\\.\\d+)?) knowledge-based',
                'pace_hours': r'PACE Credits: Maximum of (\\d+(?:\\.\\d+)?) of PACE',
                'ce_broker_hours': r'CE Broker: Maximum of (\\d+(?:\\.\\d+)?) CE broker'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, credit_text)
                if match:
                    credits[key] = match.group(1)
            
            # ACPE Number
            acpe_match = re.search(r'ACPE Number: ([^\\n\\r]+)', credit_text)
            if acpe_match:
                credits['acpe_number'] = acpe_match.group(1).strip()
            
            return credits
            
        except Exception as e:
            logger.warning(f"Error extracting credits: {e}")
            return {}
    
    def _extract_speakers(self, tree) -> List[Dict[str, str]]:
        """Extract speaker information"""
        try:
            speakers = []
            
            # Speaker li elements
            speaker_elements = tree.xpath('//ul[@class="speakers-wrap"]//li[@class="speakerrow"]')
            
            for element in speaker_elements:
                try:
                    # Speaker name
                    name_elements = element.xpath('.//p[contains(@class, "speaker-name")]/text()')
                    name = name_elements[0].strip() if name_elements else ""
                    
                    # Presenter ID
                    presenter_id = element.get('data-presenterid', '')
                    
                    # Professional info
                    prof_elements = element.xpath('.//p[contains(@class, "prof-text")]//text()')
                    prof_parts = [text.strip() for text in prof_elements if text.strip()]
                    
                    # Parse affiliation components
                    title = prof_parts[0] if len(prof_parts) > 0 else ""
                    department = prof_parts[1] if len(prof_parts) > 1 else ""
                    institution = prof_parts[2] if len(prof_parts) > 2 else ""
                    location = prof_parts[3] if len(prof_parts) > 3 else ""
                    
                    if len(prof_parts) == 3:
                        # No department, shift everything
                        department = ""
                        institution = prof_parts[1]
                        location = prof_parts[2]
                    elif len(prof_parts) == 2:
                        # Just institution and location
                        title = ""
                        department = ""
                        institution = prof_parts[0]
                        location = prof_parts[1]
                    
                    speakers.append({
                        'name': name,
                        'presenter_id': presenter_id,
                        'title': title,
                        'department': department,
                        'institution': institution,
                        'location': location,
                        'full_affiliation': ' | '.join(prof_parts)
                    })
                    
                except Exception as speaker_error:
                    logger.warning(f"Error parsing speaker: {speaker_error}")
                    continue
            
            return speakers
            
        except Exception as e:
            logger.warning(f"Error extracting speakers: {e}")
            return []
    
    def _extract_disclosures(self, tree) -> List[Dict[str, str]]:
        """Extract disclosure information"""
        try:
            disclosures = []
            
            # Disclosure blocks
            disclosure_elements = tree.xpath('//div[@class="presentation-disclosure-block"]')
            
            for element in disclosure_elements:
                text = element.text_content().strip()
                
                # Skip header
                if text == "Disclosure(s):":
                    continue
                
                # Parse "Speaker Name: disclosure text"
                if ':' in text:
                    parts = text.split(':', 1)
                    speaker_name = parts[0].strip()
                    disclosure_text = parts[1].strip()
                    
                    # Clean speaker name (remove bold formatting)
                    speaker_name = re.sub(r'\\*\\*([^*]+)\\*\\*', r'\\1', speaker_name)
                    
                    disclosures.append({
                        'speaker': speaker_name,
                        'disclosure': disclosure_text
                    })
            
            return disclosures
            
        except Exception as e:
            logger.warning(f"Error extracting disclosures: {e}")
            return []
    
    def _extract_presentations(self, tree) -> List[Dict[str, Any]]:
        """Extract presentation information"""
        try:
            presentations = []
            
            # Presentation li elements
            pres_elements = tree.xpath('//ul[contains(@class, "list-group")]//li[contains(@class, "list-group-item")]')
            
            for element in pres_elements:
                try:
                    # Presentation ID
                    pres_id = element.get('data-presid', '')
                    
                    # Time
                    time_elements = element.xpath('.//span[@class="tipsytip"][contains(text(), "AM") or contains(text(), "PM")]/text()')
                    time_raw = time_elements[0].strip() if time_elements else ""
                    time = re.sub(r'\\s*US ET\\s*$', '', time_raw).strip()
                    
                    # Title (first text node in prestitle div)
                    title_elements = element.xpath('.//div[contains(@class, "prestitle")]/text()[1]')
                    title = title_elements[0].strip() if title_elements else ""
                    
                    # Speaker info from biopopup span
                    speaker_name_elements = element.xpath('.//span[@class="biopopup"]/text()')
                    speaker_name = speaker_name_elements[0].strip() if speaker_name_elements else ""
                    
                    # Affiliation (everything after the em dash)
                    presenter_elements = element.xpath('.//small[@class="presentation-presenters"]')
                    affiliation = ""
                    if presenter_elements:
                        presenter_text = presenter_elements[0].text_content()
                        if '–' in presenter_text:
                            affiliation = presenter_text.split('–', 1)[1].strip()
                        elif ' - ' in presenter_text:
                            affiliation = presenter_text.split(' - ', 1)[1].strip()
                    
                    presentations.append({
                        'presentation_id': pres_id,
                        'time': time,
                        'title': title,
                        'speaker': {
                            'name': speaker_name,
                            'affiliation': affiliation
                        }
                    })
                    
                except Exception as pres_error:
                    logger.warning(f"Error parsing presentation: {pres_error}")
                    continue
            
            return presentations
            
        except Exception as e:
            logger.warning(f"Error extracting presentations: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """Get parsing statistics"""
        return {
            'parsed_count': self.parsed_count,
            'error_count': self.error_count
        }


# Test with the sample
if __name__ == "__main__":
    # Test with the real HTML sample
    with open('/Users/nickrufa/Development/www/CMEU_sites/conferencecrawler/IDWEEK2025/test_session_sample.html', 'r', encoding='utf-8') as f:
        sample_html = f.read()
    
    parser = SessionHTMLParserFixed()
    result = parser.parse_session_html(sample_html)
    
    print("Fixed Parser Results:")
    print("=" * 60)
    for key, value in result.items():
        if key != 'raw_html':
            print(f"{key}: {value}")
    
    print(f"\\nParser Stats: {parser.get_stats()}")