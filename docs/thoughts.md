---
tags: [ git, github, security, features, privacy ]

---


<h1> Thinking About... </h1>

<h2> Github.com</h2>

1. User can grab token and use .gitconfig with fake information. 
2. If user use ssh, don't need to use a token.
3. If User is using a token, he/she can modify .gitconfig with any email and that email is used to sign push request. 
  
```sh
 This lead 'us' to think:
```
- Monkey can create one repository and emulate several contributions 
       
      - Users may exist or not : email@email.com

<h3> Monkey Naughty Thoughts </h3>

- Monkey can have one repo with several contributions from different users.. 

        - Oh.. this repository have a lot of contributions...  

- Monkey can be other user.. ( hidden / visual-proxy ) to the eyes of other users / visitants.

This is what I call a <span style="font-size: 32px";>AWESOME</span> Security Feature!!


