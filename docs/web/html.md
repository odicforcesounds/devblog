# HTML

- Open Graph: Metadata control 

ogp.me -> Contém varios exemplos que podem ser usados nas páginas para que as mesmas sejam apresentadas ao serem partilhadas, com conteúdo na pré-visualização.  

## Hyper Text Markup Language

O HTML é estruturado com < tags > e essas < tags >, quase sempre definem o <início> e o </ fim > do tipo de conteúdo que uma < tag >
pode conter.

```html
<!-- Define o documento do ficheiro -->
<!DOCTYPE html>
<!-- Define a lingua usada no documento -->
<html lang="en">
	<!-- Define o header (informação que serve para a metadata) e titulo -->
	<head>
		<title>Titulo da página</title>
	</head>

	<!-- Define o corpo do documento -->
	<body>
		<h1 tooltip="Coisa coiso coisada coisado">Titulo do artigo</h1>
		<p title="Descrição">Descrição do artigo</p>
	</body>
</html>
```
