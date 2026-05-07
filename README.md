# Bypass Ghost
A high-performance asynchronous security tool designed to test 403 Forbidden bypasses using path manipulation, header injection, and method tampering.
## Core Features
 * **Asynchronous Engine:** Utilizes aiohttp for high-concurrency scanning.
 * **Bypass Modules:** Automated testing for 50+ known bypass techniques.
 * **Wayback Integration:** Checks the Wayback Machine for publicly cached historical versions.
 * **Reporting:** Automatic JSON output generation for post-scan analysis.
 * **Clean Interface:** Real-time data visualization via the rich library.
## Installation
### Prerequisites
 * Python 3.8 or higher
 * pip (Python package manager)
### Setup
```bash
# Clone the repository
git clone https://github.com/alonebeast002/bypass-ghost.git
cd bypass-ghost

# Install required dependencies
pip install aiohttp rich urllib3

```
## Usage
### Basic Command
```bash
python3 ghost.py <URL> <PATH>

```
### Argument Reference
| Argument | Flag | Description |
|---|---|---|
| url | N/A | Target base URL (e.g., https://example.com) |
| path | N/A | Target endpoint (e.g., admin) |
| wordlist | -w | Path to a file containing multiple endpoints |
| concurrency | -c | Number of simultaneous requests (Default: 20) |
| header | -H | Custom headers for authentication or cookies |
| no-save | --no-save | Prevents the tool from creating a JSON report |
### Examples
```bash
# Standard scan
python3 ghost.py https://target.com dashboard

# Scan with custom session cookie
python3 ghost.py https://target.com secret -H "Cookie: session=123"

# High-speed scan using a custom wordlist
python3 ghost.py https://target.com admin -w paths.txt -c 50

```
## Technical Implementation
The tool executes three primary categories of tests:
 1. **Path Manipulation:** Tests URL encoding, path traversal, and extension spoofing.
 2. **Header Injection:** Injects various IP and URL-rewrite headers (e.g., X-Forwarded-For, X-Original-URL).
 3. **Verb Tampering:** Attempts access via alternative HTTP methods like TRACE, PUT, and PATCH.
## Disclaimer
This software is intended for legal security auditing and educational purposes only. Unauthorized testing of environments without explicit permission is illegal.
## Developer
**alonebeast002**
