let monkeyCore = Object.create({
  sites: {
    domain: "odicforcesounds.com",
    artSite: "https://art.odicforcesounds.com",
    wikiSite: "https://wiki.odicforcesounds.com",
    bookSite: "https://book.odicforcesounds.com",
    testSite: "https://test.odicforcesounds.com",
    appSite: "https://app.odicforcesounds.com"
  },
  hosting: {
    github: "https://github.com/odicforcesounds/",
    accountType: "Free"
  },
  siteUsageControl: {
    cloudflare: "https://cloudflare.com/",
    "accountType": "Free"
  },
  siteImageHosting: {
    firebase: "https://firebase.com", 
    accountType: "Free"
  }
}); 

console.log(monkeyCore.sites.wikiSite)
