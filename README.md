# 🟡 GialloZafferano
Scraping ricette di Giallo Zafferano forked from [Biolazard repository](https://github.com/Biolazard/GialloZafferano)

## Utilizzo

Crea un file `secrets.py` con all'interno questa variabile e modificatela con il vostro endpoint:

```py
API_URL="your_api_endpoint"
```

* La struttura dell'endpoint sarà questa: `https://www.API_URL/<file>/<operation>/<sql_table_name>`. Nel mio caso:

```py
"https://www.API_URL/ricette.php/insert/ricette_rating"
```
---

## Esempio php

```php
<?php
// Connessione al database
$hostname = '';
$username = '';
$password = '';
$database = '';

$conn = new mysqli($hostname, $username, $password, $database);

if ($conn->connect_error) {
    die("Connessione fallita: " . $conn->connect_error);
}

$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

$uri_parts = explode('?', $request_uri);
$uri_path = $uri_parts[0];

$parts = explode('/', $uri_path);

// Il 2° elemento dopo la base dell'URL è il tipo di operazione
$type = $parts[2] ?? null;
// Il 3° elemento è il nome della tabella
$table = $parts[3] ?? null;

switch ($method) {
    case 'POST':
        if ($type === 'insert' && $table) {

        	// coppia (nomeColonna, valoreColonna)
            $request_body 	= file_get_contents('php://input');
            $data 			    = json_decode($request_body, true);
            $values 		    = $data['values'] ?? [];
            $columns 		    = implode(", ", array_keys($values));
            $columnValues 	= implode("', '", $values);
        
            $values['description'] = mysqli_real_escape_string($conn, $values['description']);
            
                // preparo i valori di colonna
            $columnValues = "";
            foreach ($values as $value) {
                $columnValues .= "'" . $value . "', ";
            }
            
            $columnValues = rtrim($columnValues, ", ");
            
                // verifico se esiste gia una ricetta con quel titolo
            $check_query = "SELECT * FROM $table WHERE title = '{$values['title']}'";
            $check_result = $conn->query($check_query);
            
              if ($check_result->num_rows > 0) {
                $sql_message = "Il record esiste già nella tabella.";
            } else {
              // INSERT QUERY
              $sql_query = "INSERT INTO $table ($columns) VALUES ($columnValues)";
              if ($conn->query($sql_query) === TRUE) {
                echo "INSERT eseguita con successo";
              } else {
                echo "Errore nell'esecuzione della query: " . $conn->error . "\nQUERY: $sql_query";
              }
            } 

        }
        break;
    default:
        echo "Metodo non implementato";
        break;
}

$conn->close();
?>
```

---

## Creazione file json

Decommenta [questa linea](https://github.com/GGFalco/giallo-zafferano-scraper/blob/17519b0e031f6a73423a5e5d7bfe383bbdc1e76a/main.py#L75) di codice se vuoi creare i file .json

---

## Struttura Database

Ecco il codice MySQL per creare la tabella del database

```sql
CREATE TABLE `ricette_rating` (
  `id` int NOT NULL AUTO_INCREMENT,
  `imagebase64` longtext,
  `title` longtext,
  `category` longtext,
  `description` longtext,
  `linkToRecipe` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `ingredients` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `imageURL` longtext,
  `rating` longtext,
PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

```

### Installazione dipendenze
`python3 -m pip install -r requirements.txt`
