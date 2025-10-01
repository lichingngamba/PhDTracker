import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import pandas as pd
import time
import urllib.parse
import warnings
warnings.filterwarnings('ignore')

class PhDAdmissionCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # University websites to crawl
        self.universities = {
            'IISc Bangalore': 'https://iisc.ac.in/admissions/external-registration-programme-ph-d/',
            'REVA University': 'https://www.reva.edu.in/phd-admissions/',
            'Christ University': 'https://christuniversity.in/bangalore-central-campus-phd-programmes',
            'PES University': 'https://pes.edu/phd/',
            'CMR Institute of Technology': 'https://www.cmrit.ac.in/admissions/doctoral-programmes/',
            'Bangalore University': 'https://bangaloreuniversity.karnataka.gov.in/381/phd/en',
            'Jain University': 'https://www.jainuniversity.ac.in/program/phd/doctor-of-philosophy-phd',
            'Dayananda Sagar University': 'https://www.dsu.edu.in/dsu-research/phd-admission'
        }
        
        # Keywords to search for
        self.deadline_keywords = [
            'last date', 'deadline', 'application closes', 'submission date', 
            'final date', 'closing date', 'due date', 'apply by', 'before'
        ]
        
        # Date patterns
        self.date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+(\d{4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b'
        ]
        
        self.results = []

    def extract_dates_from_text(self, text):
        """Extract dates from text using regex patterns"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append(match.group())
        return dates

    def clean_text(self, text):
        """Clean and normalize text"""
        return ' '.join(text.split())

    def search_for_deadlines(self, soup, url):
        """Search for deadline information in the parsed HTML"""
        deadline_info = []
        
        # Search in all text elements
        all_text = soup.get_text()
        
        for keyword in self.deadline_keywords:
            # Find sentences containing deadline keywords
            sentences = re.split(r'[.!?]\s+', all_text)
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    dates = self.extract_dates_from_text(sentence)
                    if dates:
                        deadline_info.append({
                            'context': self.clean_text(sentence)[:200] + '...',
                            'dates': dates,
                            'keyword': keyword
                        })
        
        return deadline_info

    def crawl_university(self, name, url):
        """Crawl a single university website"""
        print(f"Crawling {name}...")
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Status Code: {response.status_code}, text: {response.text}")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            deadline_info = self.search_for_deadlines(soup, url)
            
            result = {
                'University': name,
                'URL': url,
                'Status': 'Successfully crawled',
                'Deadline_Info': deadline_info,
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add specific parsing for known elements
            if 'iisc.ac.in' in url:
                result.update(self.parse_iisc_specific(soup))
            elif 'reva.edu.in' in url:
                result.update(self.parse_reva_specific(soup))
            elif 'christuniversity.in' in url:
                result.update(self.parse_christ_specific(soup))
            elif 'pes.edu' in url:
                result.update(self.parse_pes_specific(soup))
            
            self.results.append(result)
            time.sleep(1)  # Be respectful to servers
            
        except Exception as e:
            self.results.append({
                'University': name,
                'URL': url,
                'Status': f'Error: {str(e)}',
                'Deadline_Info': [],
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    def parse_iisc_specific(self, soup):
        """Specific parsing for IISc"""
        info = {}
        # Look for specific deadline information
        deadline_text = soup.find_all('p', text=re.compile(r'deadline|last date', re.I))
        if deadline_text:
            info['Specific_Deadline'] = deadline_text[0].get_text()
        return info

    def parse_reva_specific(self, soup):
        """Specific parsing for REVA"""
        info = {}
        # Look for admission dates
        date_elements = soup.find_all(['span', 'div'], class_=re.compile(r'date|deadline', re.I))
        if date_elements:
            info['Specific_Deadline'] = date_elements[0].get_text()
        return info

    def parse_christ_specific(self, soup):
        """Specific parsing for Christ University"""
        info = {}
        # Look for important dates
        important_dates = soup.find_all('div', text=re.compile(r'important dates|admission', re.I))
        if important_dates:
            info['Specific_Deadline'] = important_dates[0].get_text()
        return info

    def parse_pes_specific(self, soup):
        """Specific parsing for PES University"""
        info = {}
        # Look for admission information
        admission_info = soup.find_all(['p', 'div'], text=re.compile(r'admission|apply', re.I))
        if admission_info:
            info['Specific_Deadline'] = admission_info[0].get_text()
        return info

    def search_web_for_phd_info(self, query="phd admission part time bangalore 2025"):
        """Search web for additional PhD information"""
        print(f"Searching web for: {query}")
        try:
            # Use DuckDuckGo search (doesn't require API key)
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            relevant_links = []
            
            for link in links:
                href = link.get('href')
                if href and any(domain in href for domain in ['edu.in', 'ac.in', 'university']):
                    relevant_links.append(href)
            
            return relevant_links[:5]  # Return top 5 relevant links
            
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    @property
    def crawl_all(self):
        """Crawl all universities"""
        print("Starting PhD Admission Crawler for Bangalore Universities...")
        print("="*60)
        
        for name, url in self.universities.items():
            self.crawl_university(name, url)
        
        # Also search for additional information
        additional_links = self.search_web_for_phd_info()
        print(f"Found {len(additional_links)} additional relevant links")
        print("-"*60)
        print("Crawling additional links...")
        for link in additional_links:
            print(f"Crawling additional link: {link}")
            self.crawl_university("Additional Link", link)
            
        
        print("\nCrawling completed!")
        return self.results
    @property
    def display_results(self):
        """Display results in a formatted way"""
        print("\n" + "="*80)
        print("PhD ADMISSION DEADLINES - BANGALORE UNIVERSITIES (PART-TIME)")
        print("="*80)
        
        for result in self.results:
            print(f"\n📍 {result['University']}")
            print(f"   URL: {result['URL']}")
            print(f"   Status: {result['Status']}")
            print(f"   Last Updated: {result['Last_Updated']}")
            
            if result['Deadline_Info']:
                print("   📅 Found Deadline Information:")
                for info in result['Deadline_Info']:
                    print(f"      • Keyword: {info['keyword']}")
                    print(f"      • Dates: {', '.join(info['dates'])}")
                    print(f"      • Context: {info['context']}")
                    print()
            else:
                print("   ❌ No specific deadline information found")
            
            if 'Specific_Deadline' in result:
                print(f"   🎯 Specific Info: {result['Specific_Deadline']}")
            
            print("-" * 60)
            
        output_lines = []  # List to hold flashcard markdown

        for result in self.results:
            # Front side - question
            question = f"PhD Admission Deadlines for {result['University']}"
            
            # Back side - answer with details
            answer_lines = []
            answer_lines.append(f"**URL:** {result['URL']} \n\n")
            answer_lines.append(f"**Status:** {result['Status']}\n\n")
            answer_lines.append(f"**Last Updated:** {result['Last_Updated']}\n\n")
            
            if result['Deadline_Info']:
                answer_lines.append("📅 **Found Deadline Information:**\n\n")
                for info in result['Deadline_Info']:
                    answer_lines.append(f"- **Keyword:** {info['keyword']}\n\n")
                    answer_lines.append(f"- **Dates:** {', '.join(info['dates'])}\n\n")
                    answer_lines.append(f"- **Context:** {info['context']}\n\n")
            else:
                answer_lines.append("❌ No specific deadline information found \n\n")
            
            if 'Specific_Deadline' in result:
                answer_lines.append(f"🎯 **Specific Info:** {result['Specific_Deadline']}")
            
            answer = "\n".join(answer_lines)
            
            # Mark a flashcard with front and back separated by '---'
            output_lines.append(f"## {question}\n\n{answer}\n\n---")

        # Join and print all flashcards markdown
        final_flashcards_markdown = "\n".join(output_lines)


        return final_flashcards_markdown

    def save_to_csv(self, filename='phd_admissions_bangalore.csv'):
        """Save results to CSV"""
        if not self.results:
            print("No results to save")
            return
        
        # Flatten results for CSV
        csv_data = []
        for result in self.results:
            base_row = {
                'University': result['University'],
                'URL': result['URL'],
                'Status': result['Status'],
                'Last_Updated': result['Last_Updated']
            }
            
            if result['Deadline_Info']:
                for info in result['Deadline_Info']:
                    row = base_row.copy()
                    row.update({
                        'Deadline_Keyword': info['keyword'],
                        'Found_Dates': ', '.join(info['dates']),
                        'Context': info['context']
                    })
                    csv_data.append(row)
            else:
                base_row.update({
                    'Deadline_Keyword': 'None',
                    'Found_Dates': 'None',
                    'Context': 'No deadline information found'
                })
                csv_data.append(base_row)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        print(f"\nResults saved to {filename}")
        return df

# Initialize and run the crawler
crawler = PhDAdmissionCrawler()
print("PhD Admission Crawler initialized successfully!")
print("This crawler will search for part-time PhD admission deadlines in Bangalore universities.")