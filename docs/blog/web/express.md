<h3> Expressjs </h3>

- Check [ExpressJS](https://expressjs.com/en/resources/middleware.html) Middleware
- Check [Pug API](https://pugjs.org/api/reference.html) to generate HTML 

Basic Concepts: 

| GET | Request a representation of the specified resource. Use only to retrieve data |

| POST | Request a result of content as new object | 

| PUT | Request to modify object in URI | 

| DELETE | Request server to delete specified resource | 

---


Setup a project with last features for expressjs 

```sh
$ npm install @babel/core --save-dev
$ npm install @babel/node --save-dev
$ npm install @babel/preset-env --save-dev
$ npm install nodemon --save-dev
$ npm install express --save 
$ npm install cors --save
$ npm install pug --save 
```
Setup package.json script section: 

```json
//...
  "scripts": {
    "test": "echo 'this is a test' && exit 1",
    "start": "nodemon --exec babel-node src/index.js"
    },
```
Setup local-server 

```javascript
// src/index.js
import express from 'express'; 
const app = express(); 

app.set('view engine', 'pug');
app.set('views', './views'); // create folder views 

app.get('/first_template', function(req, res) {
  res.render('firstView'); 
}); 

app.get('/', function(req, res){
  res.send('This is the main page');
});

app.post('/test', function(req, res){
  res.send("You call me from post method page route '/test'!\n"); 
}); 

app.listen(3000); 
```

Create file to render in views/firstView.pug

```pug
doctype html
html
  head
    title = "yellow Monkey"
  body
    p.greating#Monkeys Banana
```

Run Your server:  

```sh
$ npm run start 
```

Test POST request using curl: 

```sh
$ curl -X POST "http://localhost:3000/test"
```


