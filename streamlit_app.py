import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
from datetime import datetime
import subprocess
import sys

st.set_page_config(
    page_title="SEO Analyzer Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Install required packages
@st.cache_resource
def install_chromedriver():
    """Install ChromeDriver if not present"""
    try:
        # Try to install using webdriver_manager
        from webdriver_manager.chrome import ChromeDriverManager
        return True
    except:
        return False

# Custom CSS to match your original design
st.markdown("""
<style>
    :root {
        --primary: #4361ee;
        --secondary: #3f37c9;
        --success: #4cc9f0;
        --warning: #f72585;
        --danger: #e63946;
        --light: #f8f9fa;
        --dark: #212529;
        --gradient-primary: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        --gradient-success: linear-gradient(135deg, #4cc9f0 0%, #4895ef 100%);
        --gradient-warning: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
        --radius: 12px;
    }
    
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: #4cc9f0;
    }
    
    .logo {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    .title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        max-width: 1275px;
        margin: 0 auto;
        text-align: center;
    }
    
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 40px;
    }
    
    .score-card {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 30px;
    }
    
    .score-circle {
        width: 180px;
        height: 180px;
        margin: 0 auto 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        position: relative;
        box-shadow: 0 10px 30px rgba(67, 97, 238, 0.3);
    }
    
    .score-circle.good {
        background: linear-gradient(135deg, #4cc9f0 0%, #4895ef 100%);
    }
    
    .score-circle.fair {
        background: linear-gradient(135deg, #ffbe0b 0%, #fb5607 100%);
    }
    
    .score-circle.poor {
        background: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
    }
    
    .score-label {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 10px;
        color: #212529;
    }
    
    .issue-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        border-left: 5px solid #4361ee;
    }
    
    .issue-card.success {
        border-left-color: #4cc9f0;
    }
    
    .issue-card.warning {
        border-left-color: #ffbe0b;
    }
    
    .issue-card.error {
        border-left-color: #f72585;
    }
    
    .issue-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #212529;
    }
    
    .pages-container {
        margin-top: 40px;
    }
    
    .pages-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 25px;
        margin-top: 25px;
    }
    
    .page-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
        border-top: 4px solid #4361ee;
        height: 100%;
    }
    
    .page-card:hover {
        transform: translateY(-5px);
    }
    
    .page-url {
        font-weight: 600;
        color: #4361ee;
        margin-bottom: 15px;
        word-break: break-word;
        font-size: 0.9rem;
        line-height: 1.3;
    }
    
    .page-score {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .page-score.good { color: #4cc9f0; }
    .page-score.fair { color: #ffbe0b; }
    .page-score.poor { color: #f72585; }
    
    .page-load-time {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    
    .category-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 15px;
    }
    
    .badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        background: #f0f2ff;
        color: #4361ee;
    }
    
    .footer {
        text-align: center;
        margin-top: 60px;
        padding: 30px;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        color: white;
        border: none;
        padding: 18px 40px;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 auto;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .stTextInput > div > div > input {
        padding: 18px 20px;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4361ee;
        box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
    }
    
    .issue-list-item {
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .issue-icon {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    
    .issue-icon.success { background: rgba(76, 201, 240, 0.2); color: #4cc9f0; }
    .issue-icon.warning { background: rgba(255, 190, 11, 0.2); color: #fb5607; }
    .issue-icon.error { background: rgba(247, 37, 133, 0.2); color: #f72585; }
    
    .category-score-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0 auto 10px;
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
    }
    
    .tab-container {
        margin: 30px 0;
    }
    
    .tab-button {
        padding: 12px 24px;
        border: none;
        background: #f0f2ff;
        color: #4361ee;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        margin-right: 10px;
        transition: all 0.3s;
    }
    
    .tab-button.active {
        background: #4361ee;
        color: white;
    }
    
    .tab-button:hover {
        background: #3a0ca3;
        color: white;
    }
    
    .aggregate-stats {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    
    .stat-card {
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        background: #f8f9ff;
        margin-bottom: 15px;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4361ee;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Check and install ChromeDriver
# --------------------------
def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        # Try to use webdriver_manager to get ChromeDriver
        from webdriver_manager.chrome import ChromeDriverManager
        return True
    except Exception as e:
        st.warning(f"ChromeDriver not found: {e}. Using fallback mode (limited analysis).")
        return False

# --------------------------
# Selenium Driver with fallback
# --------------------------
def init_driver():
    """Initialize Selenium WebDriver with fallback"""
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Try to use webdriver_manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except:
            # Fallback to system ChromeDriver
            options.add_argument("--remote-debugging-port=9222")
            driver = webdriver.Chrome(options=options)
            return driver
    except Exception as e:
        st.error(f"Failed to initialize WebDriver: {e}")
        return None

# --------------------------
# Extract ALL internal links (without Selenium fallback)
# --------------------------
def extract_all_internal_links_with_requests(base_url, max_pages=50):
    """Extract internal links using requests instead of Selenium"""
    all_pages = set([base_url])
    to_visit = [base_url]
    visited = set()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while to_visit and len(all_pages) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
            
        try:
            status_text.text(f"Crawling: {current_url} (Found {len(all_pages)} pages)")
            response = requests.get(current_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                domain = urlparse(base_url).netloc
                
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith("#") or href.startswith("javascript") or href == "/":
                        continue
                    
                    full = urljoin(current_url, href)
                    if urlparse(full).netloc == domain:
                        # Filter out common non-content pages
                        if not re.search(r"(account|login|signup|cart|wp-admin|wp-login|checkout|admin|dashboard|\.pdf$|\.jpg$|\.png$|\.zip$)", full, re.I):
                            # Remove query parameters and fragments
                            clean_url = urlparse(full)
                            clean_url = clean_url.scheme + "://" + clean_url.netloc + clean_url.path
                            if clean_url and clean_url not in all_pages and len(all_pages) < max_pages:
                                all_pages.add(clean_url)
                                to_visit.append(clean_url)
            
            visited.add(current_url)
            progress_bar.progress(len(visited) / min(20, max_pages))
            
        except Exception as e:
            visited.add(current_url)
            continue
    
    return list(all_pages)[:max_pages]

# --------------------------
# Extract internal links (lightweight version)
# --------------------------
def extract_internal_links_simple(html, base_url):
    """Simple link extraction without Selenium"""
    soup = BeautifulSoup(html, "lxml")
    pages = set()
    domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("javascript") or href == "/":
            continue
        full = urljoin(base_url, href)
        if urlparse(full).netloc == domain:
            if not re.search(r"(account|login|signup|cart|wp-admin)", full):
                pages.add(full)
    return list(pages)

# --------------------------
# SEO Checker (same as Flask)
# --------------------------
def seo_checker(url):
    score = 100
    report = []
    warnings = []
    tips = []

    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        load_time = round(time.time() - start, 2)
        html = response.text
    except:
        return ["Unable to load website"], 0, {}, 0

    if load_time > 3:
        warnings.append(f"Slow page load time: {load_time}s")
        score -= 10
    else:
        tips.append(f"Fast Response Time: {load_time}s")

    soup = BeautifulSoup(html, "lxml")

    title = soup.find("title")
    if not title or len(title.text.strip()) < 10:
        report.append("Weak or missing <title> tag")
        score -= 10
    else:
        tips.append("Good title tag length")

    meta = soup.find("meta", attrs={"name": "description"})
    if not meta:
        report.append("Meta description missing")
        score -= 7
    else:
        tips.append("Meta description found")

    h1 = soup.find_all("h1")
    if len(h1) == 0:
        report.append("Missing H1 heading")
        score -= 13
    elif len(h1) > 1:
        warnings.append("Multiple H1 tags found")
        score -= 5

    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.get("alt")]
    if len(missing_alt) > 0:
        warnings.append(f"{len(missing_alt)} images missing ALT text")
        score -= 5

    links = soup.find_all("a")
    internal = sum(1 for a in links if a.get("href") and url in a["href"])
    if internal < 3:
        warnings.append("Low number of internal links")
        score -= 8

    css_files = soup.find_all("link", rel="stylesheet")
    js_files = soup.find_all("script", src=True)
    if len(css_files) > 10:
        warnings.append(f"Too many CSS files: {len(css_files)}")
        score -= 5
    if len(js_files) > 10:
        warnings.append(f"Too many JS files: {len(js_files)}")
        score -= 5

    mobile = soup.find("meta", attrs={"name": "viewport"})
    if not mobile:
        report.append("Not mobile-friendly")
        score -= 10

    text = soup.get_text().strip()
    if len(text) < 300:
        report.append("Very low text content")
        score -= 13

    try:
        sitemap_test = requests.get(url.rstrip("/") + "/sitemap.xml")
        if sitemap_test.status_code != 200:
            warnings.append("Sitemap not found")
            score -= 8
    except:
        warnings.append("Sitemap check failed")

    try:
        robots_test = requests.get(url.rstrip("/") + "/robots.txt")
        if robots_test.status_code != 200:
            warnings.append("robots.txt missing")
            score -= 4
    except:
        warnings.append("robots.txt check failed")

    categories = {
        "Links": max(0, 20 - (5 if internal < 3 else 0)),
        "Performance": max(0, 20 - (10 if load_time > 3 else 0)),
        "On-Page SEO": max(0, 20 - (10 if not title else 0) - (10 if not meta else 0)),
        "Social": 10,
        "Usability": max(0, 20 - (10 if not mobile else 0)),
    }

    return report + warnings + tips, max(score, 0), categories, load_time

# --------------------------
# Analyze page without Selenium
# --------------------------
def analyze_page_without_selenium(page_url):
    """Analyze page using requests instead of Selenium"""
    try:
        issues, score, categories, load_time = seo_checker(page_url)
        
        # Extract some internal links from the page
        try:
            response = requests.get(page_url, timeout=10)
            html = response.text
        except:
            html = ""
        
        return {
            "url": page_url,
            "score": score,
            "categories": categories,
            "issues": issues,
            "load_time": load_time,
            "html": html
        }
    except Exception as e:
        return {
            "url": page_url,
            "score": 0,
            "categories": {},
            "issues": ["Unable to load website"],
            "load_time": 0,
            "html": ""
        }

# --------------------------
# Aggregate issues from all pages
# --------------------------
def aggregate_all_issues(pages_data):
    """Aggregate all issues from all pages and categorize them"""
    all_issues_to_fix = []
    all_good_points = []
    all_warnings = []
    
    for page in pages_data:
        for issue in page["issues"]:
            issue_lower = issue.lower()
            if 'good' in issue_lower or 'found' in issue_lower or 'fast' in issue_lower:
                all_good_points.append(f"{page['url']}: {issue}")
            elif 'slow' in issue_lower or 'missing' in issue_lower or 'not found' in issue_lower or 'low' in issue_lower:
                all_issues_to_fix.append(f"{page['url']}: {issue}")
            else:
                all_warnings.append(f"{page['url']}: {issue}")
    
    # Remove duplicates while preserving order
    all_issues_to_fix = list(dict.fromkeys(all_issues_to_fix))
    all_good_points = list(dict.fromkeys(all_good_points))
    all_warnings = list(dict.fromkeys(all_warnings))
    
    return all_issues_to_fix, all_warnings, all_good_points

# --------------------------
# Calculate aggregate statistics
# --------------------------
def calculate_aggregate_stats(pages_data):
    """Calculate aggregate statistics for all pages"""
    if not pages_data:
        return {}
    
    total_pages = len(pages_data)
    avg_score = sum(p["score"] for p in pages_data) / total_pages
    avg_load_time = sum(p["load_time"] for p in pages_data) / total_pages
    
    # Score distribution
    excellent = sum(1 for p in pages_data if p["score"] >= 80)
    good = sum(1 for p in pages_data if 60 <= p["score"] < 80)
    poor = sum(1 for p in pages_data if p["score"] < 60)
    
    # Common issues
    all_issues = []
    for page in pages_data:
        all_issues.extend(page["issues"])
    
    issue_counts = {}
    for issue in all_issues:
        # Clean issue text
        clean_issue = issue.split(": ")[-1] if ": " in issue else issue
        issue_counts[clean_issue] = issue_counts.get(clean_issue, 0) + 1
    
    top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_pages": total_pages,
        "avg_score": round(avg_score, 1),
        "avg_load_time": round(avg_load_time, 2),
        "excellent_pages": excellent,
        "good_pages": good,
        "poor_pages": poor,
        "top_issues": top_issues
    }

# --------------------------
# Main App
# --------------------------
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="logo">🔍</div>
        <h1 class="title">SEO X-Ray – Full Website SEO Diagnostic System</h1>
        <p class="subtitle">Get detailed SEO insights for your website and ALL internal pages with comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Check ChromeDriver status
    chromedriver_available = check_chromedriver()
    
    # URL Input Form
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input("", placeholder="https://example.com", key="url_input", label_visibility="collapsed")
    
    with col2:
        analyze_button = st.button("🔍 Analyze ALL Pages SEO", use_container_width=True)
    
    if not chromedriver_available:
        st.warning("⚠️ **Note:** ChromeDriver not available. Running in fallback mode. Some JavaScript-heavy websites may not be fully analyzed.")
        mode = "lightweight"
    else:
        mode = "standard"
        st.info(f"✅ **Standard Mode Active** - Analyzing up to 50 pages")
    
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_button and url:
        if not url.startswith("http"):
            url = "https://" + url

        with st.spinner("🚀 Starting comprehensive website analysis... This may take several minutes"):
            try:
                page_results = []
                
                if mode == "standard" and chromedriver_available:
                    # Try to use Selenium for better JavaScript rendering
                    try:
                        driver = init_driver()
                        if driver:
                            st.info("🔍 Step 1/3: Crawling website with Selenium...")
                            driver.get(url)
                            time.sleep(3)
                            main_html = driver.page_source
                            
                            # Extract initial links
                            all_pages = set([url])
                            soup = BeautifulSoup(main_html, "lxml")
                            domain = urlparse(url).netloc
                            
                            for a in soup.find_all("a", href=True):
                                href = a["href"].strip()
                                if href.startswith("#") or href.startswith("javascript") or href == "/":
                                    continue
                                full = urljoin(url, href)
                                if urlparse(full).netloc == domain:
                                    if not re.search(r"(account|login|signup|cart|wp-admin)", full):
                                        all_pages.add(full)
                            
                            all_pages = list(all_pages)[:50]  # Limit to 50 pages
                            driver.quit()
                        else:
                            raise Exception("Driver initialization failed")
                            
                    except Exception as e:
                        st.warning(f"Selenium failed: {e}. Switching to fallback mode.")
                        mode = "lightweight"
                        all_pages = extract_all_internal_links_with_requests(url, max_pages=50)
                
                else:
                    # Lightweight mode using requests
                    st.info("🔍 Step 1/3: Crawling website (fallback mode)...")
                    all_pages = extract_all_internal_links_with_requests(url, max_pages=50)
                
                if not all_pages:
                    st.error("No internal pages found to analyze.")
                    return
                
                st.success(f"✅ Found {len(all_pages)} pages to analyze")
                
                # Step 2: Analyze all pages
                st.info(f"🔍 Step 2/3: Analyzing {len(all_pages)} pages...")
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Analyze pages
                for i, page in enumerate(all_pages):
                    status_text.text(f"Analyzing page {i+1}/{len(all_pages)}")
                    if mode == "standard" and chromedriver_available:
                        try:
                            driver = init_driver()
                            driver.get(page)
                            time.sleep(2)
                            page_html = driver.page_source
                            issues, score, categories, load_time = seo_checker(page)
                            driver.quit()
                            
                            page_results.append({
                                "url": page,
                                "score": score,
                                "categories": categories,
                                "issues": issues,
                                "load_time": load_time
                            })
                        except:
                            # Fallback to requests if Selenium fails
                            page_result = analyze_page_without_selenium(page)
                            page_results.append(page_result)
                    else:
                        page_result = analyze_page_without_selenium(page)
                        page_results.append(page_result)
                    
                    progress_bar.progress((i + 1) / len(all_pages))
                
                # Step 3: Analyze homepage separately
                st.info("🔍 Step 3/3: Analyzing homepage...")
                homepage_issues, homepage_score, homepage_categories, homepage_load_time = seo_checker(url)
                
                # Aggregate issues from ALL pages
                all_issues_to_fix, all_warnings, all_good_points = aggregate_all_issues(page_results)
                
                # Calculate aggregate statistics
                aggregate_stats = calculate_aggregate_stats(page_results)
                
                # Store results in session state
                st.session_state.result = {
                    "homepage_score": homepage_score,
                    "homepage_issues": homepage_issues,
                    "homepage_categories": homepage_categories,
                    "pages": page_results,
                    "analyzed_url": url,
                    "all_issues_to_fix": all_issues_to_fix,
                    "all_warnings": all_warnings,
                    "all_good_points": all_good_points,
                    "aggregate_stats": aggregate_stats,
                    "mode": mode
                }
                
                st.balloons()
                st.success(f"✅ Analysis complete! Analyzed {len(page_results)} pages.")
                
            except Exception as e:
                st.error(f"Error analyzing website: {str(e)}")
                return

    # Display Results
    if "result" in st.session_state:
        result = st.session_state.result
        
        # Display mode info
        if result.get("mode") == "lightweight":
            st.info("📱 **Fallback Mode**: Analysis performed without browser automation. Some dynamic content may not be captured.")
        
        # Tabs for different views
        tabs = st.tabs(["🏠 Homepage Analysis", "📊 All Pages Overview", "⚠️ All Issues to Fix", "✅ All Good Points"])
        
        with tabs[0]:  # Homepage Analysis
            # Homepage Score
            st.markdown("""
            <div class="score-card">
                <h2 style="margin-bottom: 20px; color: #4361ee;">Homepage Score</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if result["homepage_score"] >= 80:
                    score_class = "good"
                    score_message = "Excellent! Your homepage is well optimized"
                elif result["homepage_score"] >= 60:
                    score_class = "fair"
                    score_message = "Good, but there's room for improvement"
                else:
                    score_class = "poor"
                    score_message = "Needs significant improvement"
                
                st.markdown(f"""
                <div class="score-circle pulse {score_class}">
                    {result["homepage_score"]}/100
                </div>
                <div class="score-label">
                    {score_message}
                </div>
                """, unsafe_allow_html=True)
            
            # Homepage Issues
            st.markdown("## 📊 Homepage Analysis Results")
            
            issue_types = {'success': [], 'warning': [], 'error': []}
            for issue in result["homepage_issues"]:
                issue_lower = issue.lower()
                if 'good' in issue_lower or 'found' in issue_lower or 'fast' in issue_lower:
                    issue_types['success'].append(issue)
                elif 'slow' in issue_lower or 'missing' in issue_lower or 'not found' in issue_lower or 'low' in issue_lower:
                    issue_types['error'].append(issue)
                else:
                    issue_types['warning'].append(issue)
            
            cols = st.columns(3)
            issue_data = [
                ("error", "❌", "Issues to Fix", issue_types['error']),
                ("warning", "⚠️", "Warnings", issue_types['warning']),
                ("success", "✅", "Good Points", issue_types['success'])
            ]
            
            for idx, (issue_type, icon, title, issues) in enumerate(issue_data):
                if issues:
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="issue-card {issue_type}">
                            <div class="issue-title">
                                {icon} {title}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for issue in issues:
                            icon_html = ""
                            if issue_type == 'success':
                                icon_html = '<div class="issue-icon success">✓</div>'
                            elif issue_type == 'warning':
                                icon_html = '<div class="issue-icon warning">!</div>'
                            else:
                                icon_html = '<div class="issue-icon error">✗</div>'
                            
                            st.markdown(f"""
                            <div class="issue-list-item">
                                {icon_html}
                                <span>{issue}</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Category Scores
            if result["homepage_categories"]:
                st.markdown("## 📈 SEO Category Breakdown")
                cols = st.columns(len(result["homepage_categories"]))
                for idx, (category, score) in enumerate(result["homepage_categories"].items()):
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.8rem; font-weight: 600; margin: 0 auto 10px;">
                                {score}/20
                            </div>
                            <div style="font-weight: 600; color: #212529;">{category}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tabs[1]:  # All Pages Overview
            # Aggregate Statistics
            if "aggregate_stats" in result:
                stats = result["aggregate_stats"]
                st.markdown("## 📊 All Pages Aggregate Statistics")
                
                cols = st.columns(4)
                with cols[0]:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_pages']}</div>
                        <div class="stat-label">Total Pages Analyzed</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{stats['avg_score']}</div>
                        <div class="stat-label">Average SEO Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{stats['excellent_pages']}</div>
                        <div class="stat-label">Excellent Pages (≥80)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{stats['avg_load_time']}s</div>
                        <div class="stat-label">Avg Load Time</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Score Distribution
                st.markdown("### 📈 Score Distribution Across All Pages")
                score_data = {
                    "Excellent (80-100)": stats["excellent_pages"],
                    "Good (60-79)": stats["good_pages"],
                    "Poor (0-59)": stats["poor_pages"]
                }
                
                import plotly.graph_objects as go
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(score_data.keys()),
                        y=list(score_data.values()),
                        marker_color=['#4cc9f0', '#ffbe0b', '#f72585']
                    )
                ])
                fig.update_layout(
                    title="SEO Score Distribution",
                    xaxis_title="Score Range",
                    yaxis_title="Number of Pages",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # All Pages Grid
            st.markdown(f"## 🌐 All Pages Analysis ({len(result['pages'])} pages)")
            
            # Sort pages by score
            sorted_pages = sorted(result["pages"], key=lambda x: x["score"], reverse=True)
            
            # Create grid
            cols = st.columns(2)
            for idx, page in enumerate(sorted_pages):
                col_idx = idx % 2
                with cols[col_idx]:
                    if page["score"] >= 80:
                        score_color = "#4cc9f0"
                    elif page["score"] >= 60:
                        score_color = "#ffbe0b"
                    else:
                        score_color = "#f72585"
                    
                    # Truncate URL for display
                    display_url = page['url']
                    if len(display_url) > 40:
                        display_url = display_url[:37] + "..."
                    
                    page_card = f"""
                    <div class="page-card">
                        <div class="page-url" title="{page['url']}">{display_url}</div>
                        <div class="page-score" style="color: {score_color};">
                            {page['score']}/100
                        </div>
                        <div class="page-load-time">
                            ⏱️ Load time: {page['load_time']}s
                        </div>
                        <div style="margin-top: 10px; font-size: 0.85rem; color: #666;">
                            📊 {len(page['issues'])} issues found
                        </div>
                    """
                    
                    # Add category badges
                    if page["categories"]:
                        badges_html = ""
                        for category, score_val in page["categories"].items():
                            badges_html += f'<div class="badge">{category}: {score_val}/20</div>'
                        page_card += f'<div class="category-badges">{badges_html}</div>'
                    
                    page_card += "</div>"
                    st.markdown(page_card, unsafe_allow_html=True)
        
        with tabs[2]:  # All Issues to Fix
            st.markdown("## ⚠️ All Issues to Fix Across All Pages")
            st.markdown(f"### Found {len(result['all_issues_to_fix'])} unique issues across {len(result['pages'])} pages")
            
            if result['all_issues_to_fix']:
                # Display issues with expandable sections
                for i, issue in enumerate(result['all_issues_to_fix'][:50]):  # Limit to 50 issues
                    with st.expander(f"🔴 Issue {i+1}: {issue[:100]}...", expanded=i < 3):
                        st.markdown(f"""
                        <div style="padding: 15px; margin: 5px 0; background: #fff5f5; border-radius: 8px; border-left: 4px solid #f72585;">
                            <div style="display: flex; align-items: start; gap: 10px;">
                                <div style="color: #f72585; font-size: 1.5rem; font-weight: bold;">✗</div>
                                <div>
                                    <strong style="color: #f72585;">Issue:</strong><br>
                                    {issue}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("🎉 No critical issues found across all pages!")
        
        with tabs[3]:  # All Good Points
            st.markdown("## ✅ All Good Points Across All Pages")
            st.markdown(f"### Found {len(result['all_good_points'])} positive points across {len(result['pages'])} pages")
            
            if result['all_good_points']:
                # Display good points with expandable sections
                for i, point in enumerate(result['all_good_points'][:50]):  # Limit to 50 points
                    with st.expander(f"🟢 Good Point {i+1}: {point[:100]}...", expanded=i < 3):
                        st.markdown(f"""
                        <div style="padding: 15px; margin: 5px 0; background: #f0fff4; border-radius: 8px; border-left: 4px solid #4cc9f0;">
                            <div style="display: flex; align-items: start; gap: 10px;">
                                <div style="color: #4cc9f0; font-size: 1.5rem; font-weight: bold;">✓</div>
                                <div>
                                    <strong style="color: #4cc9f0;">Good Practice:</strong><br>
                                    {point}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No specific good points identified. Focus on fixing the issues above.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>SEO Analyzer Pro &copy; {year} | Powered by Streamlit & BeautifulSoup</p>
        <p style="margin-top: 10px; font-size: 0.8rem;">
            ⚡ Analyzes ALL internal pages automatically (up to 50 pages)
        </p>
    </div>
    """.format(year=datetime.now().year), unsafe_allow_html=True)

if __name__ == "__main__":
    # Try to install webdriver_manager if not present
    try:
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        st.warning("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver_manager"])
    
    main()
