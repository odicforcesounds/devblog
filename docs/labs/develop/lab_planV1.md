<h2> Prepare Lab to Develop </h2>

1. Machine to code: any distro / OS
2. Machine to test: linux
3. Machine to host: linux

---

<h3> Machine to Code </h3>

```
Only need a Code Editor: vim / vscode / sublime / atom / etc....
```

- We use vim for non-graphical use.
- IP: 192.168.200.100
- Not sharing any service ( client )
- Install NodeJS ( optional )

<h3> Machine to Test and Develop </h3>

```
This machine needs to run the web-server and database.
```

- We may use debian based distros to make things easier to install and configure.
- IP: 192.168.200.150
- Sharing ssh-server, web-server and db-server
- Install NodeJS and MongoDB ( local-web-servers)
- Configure MongoDB ( create database )

<h3>Machine to Host </h3>

``` 
This host is used to give us extra space to backup lab files ( git-commits )
```
- IP: 192.168.200.200
- Sharing ssh-server ( local-git-server )
- Not necessarily a public server, but a private one. 