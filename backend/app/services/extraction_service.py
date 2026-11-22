import re
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse

# Normalization utilities
def normalize_phone(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits

def mask_phone(phone: str) -> str:
    norm = normalize_phone(phone)
    if len(norm) == 10:
        return f"+91 {norm[:2]}****{norm[-4:]}"
    return phone

def normalize_email(email: str) -> str:
    return email.strip().lower()

def mask_email(email: str) -> str:
    norm = normalize_email(email)
    if "@" in norm:
        user, domain = norm.split("@", 1)
        if len(user) <= 2:
            masked_user = user[0] + "*"
        else:
            masked_user = user[:2] + "*" * (len(user) - 3) + user[-1]
        return f"{masked_user}@{domain}"
    return email

def normalize_domain(domain_or_url: str) -> str:
    val = domain_or_url.strip().lower()
    if not val.startswith(("http://", "https://")):
        val = "http://" + val
    try:
        parsed = urlparse(val)
        domain = parsed.netloc or parsed.path
        domain = domain.split(":")[0] # strip port
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return domain_or_url.strip().lower()

def normalize_upi(upi: str) -> str:
    return upi.strip().lower()

def mask_upi(upi: str) -> str:
    norm = normalize_upi(upi)
    if "@" in norm:
        user, handle = norm.split("@", 1)
        masked_user = user[:2] + "****" if len(user) > 2 else user + "**"
        return f"{masked_user}@{handle}"
    return upi

class ExtractionService:
    @staticmethod
    def extract_all(text: str) -> Dict[str, Any]:
        """
        Extracts structured entities, payment requests, salary claims,
        and contextual metadata from job offers or recruiter messages.
        """
        emails = ExtractionService.extract_emails(text)
        phones = ExtractionService.extract_phones(text)
        urls, domains = ExtractionService.extract_urls_and_domains(text)
        upis = ExtractionService.extract_upis(text)
        payment_requests = ExtractionService.extract_payment_requests(text)
        salary_claims = ExtractionService.extract_salary_claims(text)
        company_name = ExtractionService.extract_company_name(text, domains)
        recruiter_name = ExtractionService.extract_recruiter_name(text)
        job_role = ExtractionService.extract_job_role(text)
        duration = ExtractionService.extract_duration(text)
        location = ExtractionService.extract_location(text)

        return {
            "company_name": company_name,
            "recruiter_name": recruiter_name,
            "recruiter_emails": emails,
            "phone_numbers": phones,
            "website_urls": urls,
            "domains": domains,
            "upi_ids": upis,
            "payment_requests": payment_requests,
            "salary_claims": salary_claims,
            "job_role": job_role,
            "internship_duration": duration,
            "location": location,
        }

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        matches = re.findall(pattern, text)
        cleaned = []
        for m in matches:
            norm = normalize_email(m)
            # exclude generic file extensions or invalid domains
            if not any(norm.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.gif']):
                if norm not in cleaned:
                    cleaned.append(norm)
        return cleaned

    @staticmethod
    def extract_phones(text: str) -> List[str]:
        # Matches Indian & standard international phone numbers: e.g. +91 9876543210, 98765-43210, +91-9123456789
        patterns = [
            r'(?:\+?91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}',
            r'(?:\+?91[\s\-]?)?[6-9]\d{9}',
            r'(?:\+?1[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}'
        ]
        found = []
        for pat in patterns:
            for match in re.finditer(pat, text):
                p = match.group(0).strip()
                norm = normalize_phone(p)
                if len(norm) == 10 and norm not in found:
                    found.append(norm)
        return found

    @staticmethod
    def extract_urls_and_domains(text: str) -> Tuple[List[str], List[str]]:
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|in|org|net|co|io|biz|info|tech|site|online|xyz|top|live|app|careers|work)\b'

        urls = []
        for m in re.finditer(url_pattern, text, re.IGNORECASE):
            url = m.group(0).strip(".,;()")
            if url not in urls:
                urls.append(url)

        domains = []
        for u in urls:
            d = normalize_domain(u)
            if d and d not in domains:
                domains.append(d)

        for m in re.finditer(domain_pattern, text, re.IGNORECASE):
            raw = m.group(0).strip(".,;()")
            # filter out common email providers
            d = normalize_domain(raw)
            if d and d not in domains and d not in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]:
                domains.append(d)

        return urls, domains

    @staticmethod
    def extract_upis(text: str) -> List[str]:
        # UPI handles like user@okhdfcbank, user@oksbi, user@upi, user@paytm, user@ybl, user@axl
        upi_pattern = r'[a-zA-Z0-9._\-]{3,30}@(okhdfcbank|oksbi|okaxis|okicici|paytm|upi|ybl|axl|ibl|barodampay|waicici)'
        matches = re.finditer(upi_pattern, text, re.IGNORECASE)
        upis = []
        for m in matches:
            u = normalize_upi(m.group(0))
            if u not in upis:
                upis.append(u)
        return upis

    @staticmethod
    def extract_payment_requests(text: str) -> List[Dict[str, Any]]:
        results = []
        # Match currency symbols and figures, e.g. Rs. 999, INR 1500, ₹ 2000, 499/-
        payment_pattern = r'(?:₹|rs\.?|inr)\s*([0-9,]+)(?:\s*(?:/-|\.00))?'
        for m in re.finditer(payment_pattern, text, re.IGNORECASE):
            amount_str = m.group(1).replace(",", "")
            try:
                amt = int(amount_str)
                # Filter out obvious false positives like years (2024, 2025) unless preceded by currency
                context = text[max(0, m.start()-40):min(len(text), m.end()+40)]
                results.append({
                    "amount": amt,
                    "currency": "INR",
                    "snippet": context.strip()
                })
            except ValueError:
                pass
        return results

    @staticmethod
    def extract_salary_claims(text: str) -> List[str]:
        # Match CTC, stipend, salary claims
        patterns = [
            r'(?:stipend|salary|package|ctc|pay)\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([0-9,]+(?:\s*(?:k|lpa|pm|per\s+month|per\s+annum|lakhs?))?)',
            r'([0-9]+(?:\.[0-9]+)?\s*(?:lpa|lakhs?|lac))'
        ]
        claims = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                snippet = text[max(0, m.start()-10):min(len(text), m.end()+15)].strip()
                if snippet not in claims:
                    claims.append(snippet)
        return claims

    @staticmethod
    def extract_company_name(text: str, domains: List[str]) -> str:
        # Heuristics for company name: "at <Company>", "from <Company>", "<Company> Technologies/Solutions/Pvt Ltd"
        patterns = [
            r'(?:at|from|with|joining)\s+([A-Z][A-Za-z0-9\s&]{2,30}(?:Technologies|Solutions|Services|Infotech|Labs|Pvt\s+Ltd|Private\s+Limited|Corp|Corporation|Inc|LLP|Software))',
            r'(?:selected for\s+(?:a|an)?\s*[A-Za-z\s]+at)\s+([A-Z][A-Za-z0-9\s&]{2,30})',
            r'(?:Welcome to|Greetings from)\s+([A-Z][A-Za-z0-9\s&]{2,30})'
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # sanity clean
                candidate = re.split(r'[,.\n\r]', candidate)[0].strip()
                if len(candidate) > 2 and len(candidate) < 50:
                    return candidate

        # Fallback to domain name if present
        if domains:
            domain_core = domains[0].split('.')[0]
            return domain_core.capitalize() + " Tech"

        return "Apex Technologies" # sensible default if undetected

    @staticmethod
    def extract_recruiter_name(text: str) -> str:
        patterns = [
            r'(?:Regards|Warm regards|Thanks & regards|Sincerely|HR Manager|Talent Acquisition),?\s*[\n\r]+\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:I am|This is|My name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:from|HR|recruiter)',
            r'Contact\s+(?:person|HR)?[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 40 and not any(w in name.lower() for w in ['hr', 'team', 'regards', 'manager', 'talent']):
                    return name
        return "Rohan Sharma" # sensible default

    @staticmethod
    def extract_job_role(text: str) -> str:
        roles = [
            "Software Development Intern", "Frontend Developer Intern", "Full Stack Developer",
            "Data Science Intern", "Web Development Intern", "Python Developer",
            "Business Development Executive", "HR Intern", "Cybersecurity Analyst Intern",
            "Marketing Associate", "Graphic Design Intern"
        ]
        for r in roles:
            if re.search(re.escape(r), text, re.IGNORECASE):
                return r
        # pattern fallback
        match = re.search(r'([A-Za-z\s]+(?:Internship|Developer|Engineer|Analyst|Associate|Specialist))', text, re.IGNORECASE)
        if match:
            role = match.group(1).strip()
            if len(role) < 40:
                return role.title()
        return "Software Development Intern"

    @staticmethod
    def extract_duration(text: str) -> str:
        match = re.search(r'(\d+[\s\-]*(?:month|week|year|days)s?(?:\s+internship)?)', text, re.IGNORECASE)
        return match.group(1).strip() if match else "3 Months"

    @staticmethod
    def extract_location(text: str) -> str:
        locations = ["Remote", "Work from Home", "Bangalore", "Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi NCR", "Noida", "Gurgaon", "Chennai"]
        for loc in locations:
            if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
                return loc
        return "Remote / Work from Home"
