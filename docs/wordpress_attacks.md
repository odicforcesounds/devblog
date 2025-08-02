# Wordpress Attacks

[WPScan](https://wpscan.com/wordpress-cli-scanner/) is one of the free tools used to attack Wordpress websites. 

[WPRecon](https://github.com/ffx64/wprecon) is another tool used to explore websites based on Wordpress. 

If You are using CloudFlare services, you can add a **Rule** that use HTTP v1.0 and use some common paths from Wordpress. 

- site.io/wp-content/* 
- site.io/wp-admin/* 
- site.io/*.php

etc..

After adding this, you can select all continent's or specific contries. 

What Ever is your choice, you can now redirect all those attacks, to some place. 

Can be [inside](./mar.md) of your domain or [outside](./hard_decisions.md). 

My suggestion is that you redirect all malicious requests to somewhere outside your domains.. 

Is better to have low number of visits and being real persons, that automated visits that are not Bots or Crawlers. 


