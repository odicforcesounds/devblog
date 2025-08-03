# Wordpress Attacks

[WPScan](https://wpscan.com/wordpress-cli-scanner/) is one of the free tools used to attack Wordpress websites. 

[WPRecon](https://github.com/ffx64/wprecon) is another tool used to explore websites based on Wordpress. 

If You are using CloudFlare services, you can add a **Rule** that use HTTP v1.0 and use some common paths from Wordpress. 

Here is the Rule I am using right now: 

```
(http.request.version eq "HTTP/1.0") or 
(http.request.full_uri wildcard r"http://odicforcesounds.com/*.php*") or 
(http.request.uri.path wildcard r"/*php") or 
(http.request.uri.path wildcard r"/wp-admin/*") or 
(http.request.uri.path wildcard r"/wp-content/*" and ip.src.continent eq "OC") or 
(ip.src.continent eq "AF") or 
(ip.src.continent eq "AS") or 
(ip.src.continent eq "AN") or 
(ip.src.continent eq "SA") or 
(ip.src.continent eq "T1") or 
(ip.src.continent eq "NA") or 
(ip.src.country eq "IE") or 
(ip.src.country eq "FR") or 
(ip.src.country eq "AU") or 
(http.request.uri.path wildcard r"/backend/*") or 
(http.request.uri.path wildcard r"/static/*") or 
(http.request.uri.path wildcard r"/vendor/*") or 
(http.request.uri.path wildcard r"/api/*") or 
(http.request.uri.path wildcard r"/application/*") or 
(http.request.uri.path wildcard r"/app/*") or 
(http.request.uri.path wildcard r"/config/") or 
(http.request.uri.path wildcard r"/*php7")
```

I am about to create this rule for each country that try to attack me but personalized: 

- IF country === Ireland ( Redirect to Europol ) 
- IF country === USA ( redirect to FBI ) 
- ETC ... 

What Ever is your choice, you can now redirect all those attacks, to some place. 

Can be [inside](./mar.md) of your domain or [outside](./hard_decisions.md). 

My suggestion is that you redirect all malicious requests to somewhere outside your domains.. 

Is better to have low number of visits and being real persons, than automated visits that are not Bots or Crawlers. 

Trully, I dislike that choice, where I redirect all malicious atttacks to some police force.

I decided to redirect them to my own [GitHub Repository](https://github.com/odicforcesounds/)


