"""Multi-source job scrapers for Dice, LinkedIn, and Indeed.

This module provides scrapers for major job sites to enhance job search coverage.
Uses respectful scraping practices with rate limiting and proper headers.
"""

import asyncio
import httpx
import time
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import json


class JobScraper:
    """Base class for job site scrapers with common functionality."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.rate_limit_delay = 2  # seconds between requests
    
    async def _make_request(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """Make a rate-limited request with proper error handling."""
        try:
            await asyncio.sleep(self.rate_limit_delay)
            response = await client.get(url, headers=self.headers, timeout=15.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed for {url}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might break JSON
        text = re.sub(r'[^\w\s.,!?()-]', '', text)
        return text[:500]  # Limit length


class DiceScraper(JobScraper):
    """Scraper for Dice.com job postings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.dice.com"
    
    async def search_jobs(self, query: str, location: str = "United States", limit: int = 10) -> List[Dict]:
        """Search for jobs on Dice.com."""
        jobs = []
        
        # Dice search URL format
        search_url = f"{self.base_url}/jobs?q={quote_plus(query)}&location={quote_plus(location)}&radius=30&radiusUnit=mi&page=1&pageSize={min(limit, 50)}"
        
        async with httpx.AsyncClient() as client:
            html = await self._make_request(search_url, client)
            if not html:
                return jobs
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards (Dice uses specific class names)
            job_cards = soup.find_all('div', class_='card')[:limit]
            
            for card in job_cards:
                try:
                    # Extract job details
                    title_elem = card.find('a', attrs={'data-cy': 'card-title-link'})
                    company_elem = card.find('a', attrs={'data-cy': 'card-company'})
                    location_elem = card.find('li', attrs={'data-cy': 'card-location'})
                    
                    if title_elem and company_elem:
                        job = {
                            'source': 'Dice',
                            'title': self._clean_text(title_elem.get_text()),
                            'company': self._clean_text(company_elem.get_text()),
                            'location': self._clean_text(location_elem.get_text() if location_elem else 'Remote'),
                            'url': urljoin(self.base_url, title_elem.get('href', '')),
                            'description': self._clean_text(card.get_text()),
                            'id': f"dice_{hash(title_elem.get('href', ''))}"
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"Error parsing Dice job card: {e}")
                    continue
        
        return jobs


class IndeedScraper(JobScraper):
    """Scraper for Indeed.com job postings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.indeed.com"
    
    async def search_jobs(self, query: str, location: str = "United States", limit: int = 10) -> List[Dict]:
        """Search for jobs on Indeed.com."""
        jobs = []
        
        # Indeed search URL format
        search_url = f"{self.base_url}/jobs?q={quote_plus(query)}&l={quote_plus(location)}&limit={min(limit, 50)}"
        
        async with httpx.AsyncClient() as client:
            html = await self._make_request(search_url, client)
            if not html:
                return jobs
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards (Indeed structure)
            job_cards = soup.find_all('div', class_='job_seen_beacon')[:limit]
            if not job_cards:
                job_cards = soup.find_all('a', attrs={'data-jk': True})[:limit]
            
            for card in job_cards:
                try:
                    # Extract job details
                    title_elem = card.find('h2', class_='jobTitle') or card.find('span', attrs={'title': True})
                    company_elem = card.find('span', class_='companyName') or card.find('a', attrs={'data-testid': 'company-name'})
                    location_elem = card.find('div', attrs={'data-testid': 'job-location'})
                    
                    # Get job link
                    link_elem = card.find('a', attrs={'data-jk': True}) or title_elem
                    job_url = ""
                    if link_elem and link_elem.get('href'):
                        job_url = urljoin(self.base_url, link_elem.get('href'))
                    
                    if title_elem and company_elem:
                        job = {
                            'source': 'Indeed',
                            'title': self._clean_text(title_elem.get_text()),
                            'company': self._clean_text(company_elem.get_text()),
                            'location': self._clean_text(location_elem.get_text() if location_elem else 'Remote'),
                            'url': job_url,
                            'description': self._clean_text(card.get_text()),
                            'id': f"indeed_{hash(job_url or title_elem.get_text())}"
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"Error parsing Indeed job card: {e}")
                    continue
        
        return jobs


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn job postings (public search)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.linkedin.com"
        self.rate_limit_delay = 3  # LinkedIn is more strict
    
    async def search_jobs(self, query: str, location: str = "United States", limit: int = 10) -> List[Dict]:
        """Search for jobs on LinkedIn (public search)."""
        jobs = []
        
        # LinkedIn public job search URL
        search_url = f"{self.base_url}/jobs/search?keywords={quote_plus(query)}&location={quote_plus(location)}&f_TPR=r86400"
        
        async with httpx.AsyncClient() as client:
            html = await self._make_request(search_url, client)
            if not html:
                return jobs
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards (LinkedIn structure)
            job_cards = soup.find_all('div', class_='base-card')[:limit]
            if not job_cards:
                job_cards = soup.find_all('li', class_='result-card')[:limit]
            
            for card in job_cards:
                try:
                    # Extract job details
                    title_elem = card.find('h3', class_='base-search-card__title') or card.find('h4', class_='result-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle') or card.find('h3', class_='result-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location') or card.find('span', class_='result-card__location')
                    
                    # Get job link
                    link_elem = card.find('a', class_='base-card__full-link') or card.find('a', href=True)
                    job_url = ""
                    if link_elem and link_elem.get('href'):
                        job_url = urljoin(self.base_url, link_elem.get('href'))
                    
                    if title_elem and company_elem:
                        job = {
                            'source': 'LinkedIn',
                            'title': self._clean_text(title_elem.get_text()),
                            'company': self._clean_text(company_elem.get_text()),
                            'location': self._clean_text(location_elem.get_text() if location_elem else 'Remote'),
                            'url': job_url,
                            'description': self._clean_text(card.get_text()),
                            'id': f"linkedin_{hash(job_url or title_elem.get_text())}"
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"Error parsing LinkedIn job card: {e}")
                    continue
        
        return jobs


class MultiSourceJobScraper:
    """Aggregates jobs from multiple sources."""
    
    def __init__(self):
        self.dice_scraper = DiceScraper()
        self.indeed_scraper = IndeedScraper()
        self.linkedin_scraper = LinkedInScraper()
    
    async def search_all_sources(self, query: str, location: str = "United States", limit_per_source: int = 10) -> List[Dict]:
        """Search all job sources concurrently and combine results."""
        
        # Create tasks for concurrent execution
        tasks = [
            self.dice_scraper.search_jobs(query, location, limit_per_source),
            self.indeed_scraper.search_jobs(query, location, limit_per_source),
            self.linkedin_scraper.search_jobs(query, location, limit_per_source)
        ]
        
        try:
            # Execute all scrapers concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_jobs = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    source_name = ['Dice', 'Indeed', 'LinkedIn'][i]
                    print(f"Error scraping {source_name}: {result}")
                    continue
                
                if isinstance(result, list):
                    all_jobs.extend(result)
            
            # Remove duplicates based on title and company
            seen = set()
            unique_jobs = []
            
            for job in all_jobs:
                job_key = (job.get('title', '').lower(), job.get('company', '').lower())
                if job_key not in seen and job.get('title') and job.get('company'):
                    seen.add(job_key)
                    unique_jobs.append(job)
            
            return unique_jobs
            
        except Exception as e:
            print(f"Error in multi-source search: {e}")
            return []


# Global instance for easy import
multi_scraper = MultiSourceJobScraper()


async def search_jobs_multi_source(query: str, location: str = "United States", limit: int = 30) -> List[Dict]:
    """
    Convenience function to search multiple job sources.
    
    Args:
        query: Job search query (e.g., "data engineer")
        location: Location filter (default: "United States")
        limit: Total limit of jobs to return
    
    Returns:
        List of job dictionaries with source information
    """
    limit_per_source = max(1, limit // 3)  # Distribute limit across sources
    return await multi_scraper.search_all_sources(query, location, limit_per_source)