// COMMENT
fetch('https://api.github.com/repos/rakzhodekams/docblog/commits')
  .then(response => response.json())
  .then(commits => alert(commits[0].author.login)); 
