JavaScript 

- Run inside Browser ( inside V8 - Compiler ) 

- Add code inside < script ></ script > tags or into file.js

- Documentation: 

| [MDN](https://developer.mozilla.org/en-US/docs/Web/javascript) | Official Documentation from Mozilla Developers Network | 

| [Free Book](https://javascript.info/) | One of the most recommended book to learn JavaScript | 

| ES5 | ES6 | 

- Versions of EcmaScript Specification
- Actualy we can use ES6 
      - is supported by the majority of more used browsers.
      - Firefox, chromium, safari

**HTML5** use several APIs. We can interact with them using JavaScript. 

Some notes: 

- You cannot test JavaScript code with nodejs ( most of the cases it doesn't work ) 

1. Create folder to work with JavaScript
2. Install recommended packages.

```sh
$ sudo npm i -g live-server eslint
```


Create index.html

```sh
$ mkdir jsTest
$ cd jsTest
$ touch index.html fetch.js
```

Now add the next content to those files

```html
<DOCTYPE html>
<html lang=en>
  <head>
    <titile> Using Fetch API </title>
  </head>
  <body>
  <script src="fetch.js"></script>
  </body>
</html>
```

Create fetch.js
```javascript
// Using Promises syntax

fetch('https://api.github.com/repos/user/repo/commits')
  .then(response => response.json())
  .then(commits => alert(commits[0].author.logon)); 
```

Run 'live-server' inside that folder and see the results

