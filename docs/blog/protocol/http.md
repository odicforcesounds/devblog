<p>Monkey Talk to Monkey using Internet like Computers do  </p>

<h5> Monkey Focus... </h5>

![](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview/fetching_a_page.png)

- Understand the details before using [NodeJS](../web/nodejs.md) and [ExpressJS](../web/express.md)

[HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) Protocol

| HTTP | Option  | Reference                                                 |
| ---- | ------- | --------------------------------------------------------- |
| X    | Methods | https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods |
| X    | Headers | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers |
| X    | CORS    | https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS    |
| X    | Cache   | https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching |
| X    | Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies |
| X    | Status  | https://developer.mozilla.org/en-US/docs/Web/HTTP/Status  |

<h2> HTTP Methods </h2>

<b>GET</b>: Ask Data to Server <br>
<b>POST</b>: Send Data to Server<br>
<b>PUT</b>: Ask Server to modify data <br>
<b>DELETE</b>: Ask Server to delete Data<br>

<h2> HTTP Header </h2>

| Host     | User-Agent | Encoding  | Language | Referer   | Connection |
| -------- | ---------- | --------- | -------- | --------- | ---------- |
| site.org | mozilla    | text/html | en       | page.html | keep-alive |

See [ALL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers) HTTP headers in detail

<h2> CORS </h2>

Server A ask to Server B some data to sent to client of Server A. Normally used to share static content.

<h2> HTTP Cache </h2>

Poem:

Data Goes and Data Comes, for each page...<br>
Therefor,<br>
Data can stay somewhere in the way....<br>
That is the Cache!<br>
It help the flow to <b>GET</b> it for your own..<br>

![](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching/http_cache_type.png)

<h2> Cookies </h2>

Cookies are not food.. Don't even taste like bananas, but Monkey use them for many things, mostly to control.

Control Sessions, user experience, user-browser-data information..

When we register / login to a website, we use cookies to save our Auth-informationm in cache / cookie.

<h2> Status Codes </h2>

| Status Code | Description           | Type                        |
| ----------- | --------------------- | --------------------------- |
| 100         | Continue              | Server Information Response |
| 101         | Switch Protocols      |                             |
| 102         | Processing WebDAV     |                             |
| 103         | Early Hints           |                             |
| 200         | Succeed               | Server Successful Responses |
| 201         | Created               |                             |
| 202         | Accepted              |                             |
| 203         | Not Authorized        |                             |
| 204         | No Content            |                             |
| 205         | Reset Content         |                             |
| 206         | Partial Content       |                             |
| 300         | Muliple Choices       | Server Redirect Messages    |
| 301         | Moved Permanently     |
| 302         | Found                 |
| 303         | See Other             |
| 304         | Not Modfied           |
| 305         | Use Proxy             |
| 306         | Unused                |
| 307         | Temporary Redirect    |
| 308         | Permanent Redirect    |
| 400         | Bad Request           | Client Error Messages       |
| 401         | Unauthorized          |
| 402         | Payment Forbidden     |
| 403         | Forbidden             |
| 404         | Not Found             |
| 405         | Method not allowed    |
| 500         | Internal Server Error | Server Error Messages       |
| 502         | Bad Gateway           |                             |
