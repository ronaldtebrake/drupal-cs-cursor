#!/usr/bin/env python3
"""
drupal_standards_to_mdc.py

This script scrapes the Drupal coding standards documentation and its subpages,
extracts each coding rule, and writes each as a separate .mdc file in the following format:

---
description: <rule description>
globs: 
---
<rule description>: <example code>

For example, for a rule with title "Casting" and description
"Put a space between the (type) and the $variable in a cast", it will generate a file called "casting.mdc" containing:

---
description: Put a space between the (type) and the $variable in a cast.
globs: 
---
Put a space between the (type) and the $variable in a cast: (int) $mynumber.

If a file already exists and the content has changed, it will update the file.

Dependencies:
  - requests
  - beautifulsoup4

Usage:
  python3 drupal_standards_to_mdc.py
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.drupal.org/docs/develop/standards"

def get_internal_links(url, base_domain):
    """
    Given a URL, returns a set of internal URLs that belong to the base domain and
    whose path starts with '/docs/develop/standards'.
    """
    links = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return links

    soup = BeautifulSoup(response.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Join relative URLs
        full_url = urljoin(url, href)
        parsed = urlparse(full_url)
        if base_domain in parsed.netloc and parsed.path.startswith("/docs/develop/standards"):
            links.add(full_url)
    return links

def crawl_standards(start_url):
    """
    Crawl the Drupal standards documentation starting from start_url.
    Returns a set of URLs (including the start_url) for all pages under the standards.
    """
    base_domain = urlparse(start_url).netloc
    visited = set()
    to_visit = set([start_url])
    
    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        print(f"Visiting: {current}")
        visited.add(current)
        new_links = get_internal_links(current, base_domain)
        # Add links that have not yet been visited
        to_visit = to_visit.union(new_links - visited)
    return visited

def sanitize_filename(title):
    """
    Given a rule title, return a safe filename (lowercase, spaces to hyphens, alphanumerics only)
    with .mdc extension.
    """
    filename = title.strip().lower()
    # Replace spaces with hyphens and remove non-alphanumeric characters (except hyphens)
    filename = re.sub(r'\s+', '-', filename)
    filename = re.sub(r'[^a-z0-9\-]', '', filename)
    return f"{filename}.mdc"

def extract_rules_from_page(url):
    """
    Given a Drupal coding standards page URL, parse the HTML and extract coding standard rules.
    This function assumes that each rule is represented by a heading (e.g. h2 or h3)
    followed by one or more paragraphs. It also looks for <pre> or <code> blocks for code examples.
    
    Returns a list of dictionaries with keys: 'title', 'description', and 'example'.
    """
    rules = []
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return rules

    soup = BeautifulSoup(response.text, "html.parser")

    # We assume rules are marked by h2 or h3 tags. Adjust selectors as needed.
    for header in soup.find_all(['h2', 'h3']):
        title = header.get_text(strip=True)
        # Simple heuristic: skip headers that are too short or generic
        if len(title) < 3 or "example" in title.lower():
            continue

        # The description will be the following sibling paragraphs until the next header.
        description_parts = []
        code_example = None
        for sibling in header.find_next_siblings():
            if sibling.name in ['h2', 'h3']:
                break
            # Collect paragraphs
            if sibling.name == "p":
                description_parts.append(sibling.get_text(strip=True))
            # Look for a code block if available
            if sibling.name in ["pre", "code"]:
                code_example = sibling.get_text(strip=True)
        if not description_parts:
            # If no paragraph found, try the immediate next element's text
            description_parts = [header.find_next().get_text(strip=True)] if header.find_next() else []
        description = " ".join(description_parts)
        # Fallback if no code example was found: use a placeholder
        if not code_example:
            code_example = "EXAMPLE_CODE_HERE"

        rule = {
            "title": title,
            "description": description,
            "example": code_example
        }
        rules.append(rule)
    return rules

def generate_mdc_content(rule):
    """
    Given a rule dictionary with keys 'title', 'description', and 'example',
    generate the .mdc file content following the rule template.
    """
    # In this template, the description is used both as metadata and as part of the code sample.
    content = (
f"---\n"
f"description: {rule['description']}\n"
f"globs: \n"
f"---\n"
f"{rule['description']}: {rule['example']}\n"
    )
    return content

def write_rule_file(rule):
    """
    Write or update a .mdc file for the given rule.
    """
    filename = sanitize_filename(rule["title"])
    new_content = generate_mdc_content(rule)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_content = f.read()
        if old_content == new_content:
            print(f"{filename} is up to date.")
            return
        else:
            print(f"Updating {filename}...")
    else:
        print(f"Creating {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    # Crawl all pages under the Drupal standards documentation
    pages = crawl_standards(BASE_URL)
    print(f"Found {len(pages)} pages to process.")
    all_rules = []
    for page in pages:
        rules = extract_rules_from_page(page)
        if rules:
            print(f"Extracted {len(rules)} rules from {page}")
            all_rules.extend(rules)
    # For each rule, create or update the corresponding .mdc file.
    for rule in all_rules:
        write_rule_file(rule)

if __name__ == "__main__":
    main()
