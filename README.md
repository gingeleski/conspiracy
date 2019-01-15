# conspiracy

Approaching fully automated web app pen tests.

Wraps Burp Suite and Chrome to automate web app pen testing.

Input:
- Pen test name
- List of URLs

Kickstarts pen test by...

- Opens Burp and sets up file for pen test (??)
- Opens Chrome and has it hooked up to Burp
- "Smoke tests" by pinging the domains
- If that's OK, it requests all of the URLs in Chrome which is going through Burp
