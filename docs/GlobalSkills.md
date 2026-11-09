# Skills: 
# 1. Create a skill for each rule. 
# 2. The sequence can be done by your choice
# 3. Cases: 
# - Case 1: Hosting is on Cloudflare
# - Case 2: Hosting is on Firebase
0. Do not expose sensible data on public or private pages. Emails, City, Names, etc. 
1. Each piece of Code should have a dedicated file. 
2. Each piece of code that use CSS, should be in a dedicated file. 
3. You can use JSON files to store public data and request them when user open any html content. 
	- This JSON files should be part of a Internal API. Not available for Public. 
4. SEO for all elements is needed. Accessibility too. 
5. Meta data only for Public "pages" is needed. 
6. A Fake account with Read only permissions is necessary to test without pushing the code. 
7. Do not touch files that are not explicitly asked. 
8. Do not change configurations without an explicity demand. 
9. You can use Public APIs (that are Free) -> Check source here: https://publicapis.dev/
10. You can add Icons or create new ones. 
11. Elements should be BIG for Phone Screens and "normal" for desktop Screens. A Script to detect that should be loaded at the first level.
12. Always make questions when you need to decide something. 
13. Local server is running for testing. Exposed with 192.168.200.10:8080 (normally)
14. If application code points to one of Firebase, use "firebase deploy"
	- It use NoSQL databases
15. If application code points to Cloudflare, use "Wrangler" tool to publish
	- It use KV databases
16. If application code do not point to the last 2 cases, just commit changes per file, per change. 
17. On every change, a commited message show be applyed. Never Push to github. 
18. Update README.md file for github projects. 
19. Refine the code and push everything for privacy and performance. 
20. Always review documentation if new features are added. 
21. For extra information or images, you can use wikipedia.org, or wikimedia.org
22. This project code is hosted on GitHub. 
	- Create commit script to add at the end of each change. 
	- The script should ask you what did change, and you explain. Never add the Agent of comments (FreeBuff Team). 
