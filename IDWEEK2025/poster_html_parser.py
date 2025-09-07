#!/usr/bin/env python3
"""
IDWeek 2025 Poster HTML Parser
Comprehensive parser for extracting poster data from IDWeek HTML content
Uses lxml with XPath for robust parsing of semi-structured HTML
"""

from lxml import html
import re
from typing import Dict, List, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PosterHTMLParser:
    """Parser for IDWeek 2025 poster HTML content using lxml XPath"""
    
    def __init__(self):
        self.parsed_count = 0
        self.error_count = 0
    
    def parse_poster_html(self, html_content: str) -> Dict[str, Any]:
        """
        Parse a complete poster HTML section and extract all relevant data
        
        Args:
            html_content (str): Raw HTML content for a single poster
            
        Returns:
            Dict containing parsed poster data
        """
        try:
            tree = html.fromstring(html_content)
            
            poster_data = {
                'track_info': self._extract_track_info(tree),
                'session_info': self._extract_session_info(tree),
                'presentation_details': self._extract_presentation_details(tree),
                'schedule': self._extract_schedule_info(tree),
                'authors': self._extract_authors(tree),
                'raw_html': html_content  # Keep for debugging
            }
            
            self.parsed_count += 1
            logger.info(f"Successfully parsed poster: {poster_data.get('presentation_details', {}).get('title', 'Unknown')}")
            
            return poster_data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error parsing poster HTML: {str(e)}")
            return {
                'error': str(e),
                'raw_html': html_content
            }
    
    def _extract_track_info(self, tree) -> Dict[str, str]:
        """Extract track information from trackname class"""
        try:
            # Track name is in span within p.trackname
            track_elements = tree.xpath('//p[contains(@class, "trackname")]//span/text()')
            track_name = track_elements[0].strip() if track_elements else ""
            
            # Extract track code if present (e.g., "B4." at the beginning)
            track_code = ""
            if track_name:
                match = re.match(r'^([A-Z]\d+\.?)\s*', track_name)
                if match:
                    track_code = match.group(1)
            
            return {
                'full_name': track_name,
                'code': track_code
            }
        except Exception as e:
            logger.warning(f"Error extracting track info: {e}")
            return {'full_name': '', 'code': ''}
    
    def _extract_session_info(self, tree) -> Dict[str, str]:
        """Extract session information from Poster Session paragraph"""
        try:
            # Session info is in the second <b> tag within a paragraph containing "Poster Session:"
            session_elements = tree.xpath('//p[contains(text(), "Poster Session:")]/b[2]/text()')
            session_type = session_elements[0].strip() if session_elements else ""
            
            return {
                'type': session_type
            }
        except Exception as e:
            logger.warning(f"Error extracting session info: {e}")
            return {'type': ''}
    
    def _extract_presentation_details(self, tree) -> Dict[str, str]:
        """Extract presentation title and ID"""
        try:
            # Title is in h1 tag
            title_elements = tree.xpath('//h1/text()')
            title = title_elements[0].strip() if title_elements else ""
            
            # Extract poster ID from title (e.g., "(P-1533)")
            poster_id = ""
            if title:
                match = re.match(r'^\(([^)]+)\)', title)
                if match:
                    poster_id = match.group(1)
                    # Remove the ID from title for clean title
                    title = re.sub(r'^\([^)]+\)\s*', '', title)
            
            return {
                'id': poster_id,
                'title': title
            }
        except Exception as e:
            logger.warning(f"Error extracting presentation details: {e}")
            return {'id': '', 'title': ''}
    
    def _extract_schedule_info(self, tree) -> Dict[str, str]:
        """Extract date, time, and location information"""
        try:
            # Date follows fa-calendar icon
            date_elements = tree.xpath('//i[contains(@class, "fa-calendar")]/following-sibling::text()[1]')
            date = date_elements[0].strip() if date_elements else ""
            
            # Time follows fa-clock-o icon
            time_elements = tree.xpath('//i[contains(@class, "fa-clock-o")]/following-sibling::text()[1]')
            time_raw = time_elements[0].strip() if time_elements else ""
            
            # Clean up time - remove "US ET" suffix if present
            time = re.sub(r'\s*US ET\s*$', '', time_raw).strip()
            timezone = "US ET" if "US ET" in time_raw else ""
            
            # Location follows fa-map-marker icon
            location_elements = tree.xpath('//i[contains(@class, "fa-map-marker")]/following-sibling::text()[1]')
            location_raw = location_elements[0].strip() if location_elements else ""
            
            # Clean up location - remove "Location: " prefix
            location = re.sub(r'^Location:\s*', '', location_raw).strip()
            
            return {
                'date': date,
                'time': time,
                'timezone': timezone,
                'location': location
            }
        except Exception as e:
            logger.warning(f"Error extracting schedule info: {e}")
            return {'date': '', 'time': '', 'timezone': '', 'location': ''}
    
    def _extract_authors(self, tree) -> Dict[str, List[Dict[str, str]]]:
        """Extract author information from the speakers-wrap section"""
        try:
            authors = {'presenting': [], 'co_authors': []}
            
            # Get all child elements of the speakers-wrap ul
            speaker_elements = tree.xpath('//ul[@class="speakers-wrap"]/*')
            current_role = None
            
            for element in speaker_elements:
                if element.tag == 'h2' and 'role-title' in element.get('class', ''):
                    # This is a role header
                    role_text = element.text_content().strip()
                    if 'Presenting' in role_text:
                        current_role = 'presenting'
                    elif 'Co-Author' in role_text:
                        current_role = 'co_authors'
                    else:
                        current_role = 'other'
                
                elif element.tag == 'li' and current_role and 'speakerrow' in element.get('class', ''):
                    # This is an author entry
                    author_info = self._parse_author_element(element)
                    if author_info and current_role in authors:
                        authors[current_role].append(author_info)
            
            return authors
            
        except Exception as e:
            logger.warning(f"Error extracting authors: {e}")
            return {'presenting': [], 'co_authors': []}
    
    def _parse_author_element(self, element) -> Optional[Dict[str, str]]:
        """Parse individual author li element"""
        try:
            # Author name is in p.speaker-name within an a tag
            name_elements = element.xpath('.//p[contains(@class, "speaker-name")]/text()')
            name = name_elements[0].strip() if name_elements else ""
            
            # Presenter ID is in data-presenterid attribute
            presenter_id = element.get('data-presenterid', '')
            
            # Affiliation info is in p.prof-text - may span multiple text nodes due to <br/> tags
            affiliation_elements = element.xpath('.//p[contains(@class, "prof-text")]//text()')
            
            # Clean and join affiliation text
            affiliation_parts = []
            for text in affiliation_elements:
                cleaned = text.strip()
                if cleaned and cleaned not in affiliation_parts:
                    affiliation_parts.append(cleaned)
            
            affiliation = ' | '.join(affiliation_parts)  # Use | as separator for multi-line affiliations
            
            # Extract individual components if possible
            title = ""
            institution = ""
            location = ""
            
            if len(affiliation_parts) >= 3:
                title = affiliation_parts[0]
                institution = affiliation_parts[1] 
                location = affiliation_parts[2]
            elif len(affiliation_parts) == 2:
                institution = affiliation_parts[0]
                location = affiliation_parts[1]
            elif len(affiliation_parts) == 1:
                institution = affiliation_parts[0]
            
            return {
                'name': name,
                'presenter_id': presenter_id,
                'affiliation_full': affiliation,
                'title': title,
                'institution': institution,
                'location': location
            }
            
        except Exception as e:
            logger.warning(f"Error parsing author element: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get parsing statistics"""
        return {
            'parsed_count': self.parsed_count,
            'error_count': self.error_count
        }


def parse_poster_batch(html_contents: List[str]) -> List[Dict[str, Any]]:
    """
    Parse multiple poster HTML contents in batch
    
    Args:
        html_contents: List of HTML strings to parse
        
    Returns:
        List of parsed poster data dictionaries
    """
    parser = PosterHTMLParser()
    results = []
    
    for i, html_content in enumerate(html_contents):
        logger.info(f"Parsing poster {i+1}/{len(html_contents)}")
        result = parser.parse_poster_html(html_content)
        results.append(result)
    
    stats = parser.get_stats()
    logger.info(f"Batch parsing complete. Parsed: {stats['parsed_count']}, Errors: {stats['error_count']}")
    
    return results


# Example usage and testing
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = '''
    <div class="col-md-12">
        <p class="trackname innertracks" style="background:#efac1f; color:#FFFFFF; font-size:14px; margin-bottom:10px; margin-right:5px;">
            <span>B4. Studies of microbial factors that govern susceptibility to microbial infection and disease</span>
        </p>
        <p><b>Poster Session: </b><b>Basic Science and Translational Studies</b></p>
        <h1>(P-1533) In silico Exploration of Cannabidiol Interactions with Outer Membrane Proteins in Salmonella Typhimurium LT2</h1>
        <div class="pull-left pres-tidbit tipsytip" title="">
            <i class="fa fa-calendar fa-fw"></i>Wednesday, October 22, 2025
        </div>
        <div class='pull-left pres-tidbit tipsytip' title=''><i class="fa fa-clock-o fa-fw"></i>12:15 PM - 1:30 PM <small>US ET</small></div>
        <div class="pull-left pres-tidbit">
            <i class="fa fa-map-marker fa-fw"></i>Location: Poster Hall B4-B5
        </div>
        
        <ul class="speakers-wrap">
            <h2 class="role-title" style="font-size: 18px;">Presenting Author(s)</h2>
            <li class="speakerrow" data-presenterid="1837106">
                <div class="photo-wrapper img-circle col-xs-2">
                    <img class='presenterphoto' src="https://www.conferenceharvester.com/uploads/harvester/photos/cropCPXYOJIQ-Presenter-RozenEisenbergI.jpg" title="Ilan Rozen Eisenberg, MD, MMS photo" />
                </div>
                <div class="col-xs-9">
                    <a class="loadbyurl" href="/ajaxcalls/posterPresenterInfo.asp?PresenterID=1837106">
                        <p class='speaker-name '>Ilan Rozen Eisenberg, MD, MMS</p>
                    </a>
                    <p class="text-muted prof-text">Clinical Fellow<br/>Boston Medical Center / Boston University<br/>Brookline, MA, United States</p>
                </div>
            </li>
            <h2 class="role-title" style="font-size: 18px;">Co-Author(s)</h2>
            <li class="speakerrow" data-presenterid="1870736">
                <div class="photo-wrapper img-circle col-xs-2 text-center no-photo relative">
                    <span class='presenterphoto-init hcenter'>YS</span>
                </div>
                <div class="col-xs-9">
                    <a class="loadbyurl" href="/ajaxcalls/posterPresenterInfo.asp?PresenterID=1870736">
                        <p class='speaker-name '>Yazdani Shaik-Dasthagirisaheb, PhD</p>
                    </a>
                    <p class="text-muted prof-text">Boston Medical Center / Boston University<br/>Boston, Massachusetts, United States</p>
                </div>
            </li>
        </ul>
    </div>
    '''
    
    # Test the parser
    parser = PosterHTMLParser()
    result = parser.parse_poster_html(sample_html)
    
    print("Parsed Result:")
    print("=" * 50)
    for key, value in result.items():
        if key != 'raw_html':  # Skip raw HTML in display
            print(f"{key}: {value}")
    
    print(f"\nParser Stats: {parser.get_stats()}")