---
title: "pl-smsplanet Documentation"
source: "https://smsplanet.pl/doc/slate/index.html"
scraped: "2026-06-24T18:01:07.689Z"
tokens: 12705
---
# pl-smsplanet Documentation

> Source: https://smsplanet.pl/doc/slate/index.html
> Generated: 6/24/2026, 8:01:07 PM

### pl-smsplanet

#### _doc_slate_index.html.md

> Source: https://smsplanet.pl/doc/slate/index.html
> Scraped: 6/24/2026, 8:01:07 PM

## Wstęp
```
`Po prawej stronie ekranu na ciemnym tle zobaczysz przykłady wywołań API.`
```
Platforma SMSPLANET umożliwia masową wysyłkę SMS-ów oraz MMS-ów marketingowych. Umożliwiamy integrację naszej platformy z dowolnym systemem komputerowym za pomocą opisanego w niniejszej dokumentacji API.

### Wersja API

2.3.0

### Kodowanie

Kodowanie znaków używane podczas komunikacji z API: **UTF-8**

### Nagłówek Content-Type

Wartość nagłówka Content-Type dla żądań typu POST: **application/x-www-form-urlencoded**

### Limity ilości przesyłanych żądań

Limit dla żądań wysyłających SMS/MMS: 1000/min
Limit dla pozostałych żądań (raporty, skracanie linków itp.): 300/min
Po przekroczeniu limitu, następuje blokada API na 60 sekund.

**Ważne! Jak nie przekroczyć limitu podczas wysyłki wiadomości? Nasze zalecenia:**

1.  Do wysyłki SMS używaj metody POST.
2.  Jeśli chcesz zrealizować masową wysyłkę do wielu odbiorców o tej samej treści - dodaj wszystkie numery w parametrze 'to'. W jednym żądaniu możesz dodać 10k numerów, co oznacza, że aby wysłać SMS do np. 100k odbiorców, wystarczy wysłać do nas 10 żądań POST, po 10k numerów w każdym żądaniu - zamiast 100k osobnych żądań.

    **W sytuacji przekroczenia ilości 30 żądań (300 000 SMS) / min, system może zacząć buforować żądania i przetwarzać je w osobnej kolejce. Więcej o buforowaniu [tutaj](_doc_slate_index.html.md#bufor).**

3.  Jeśli chcesz zrealizować masową wysyłkę do wielu odbiorców o różnej treści - zastosuj parametry 'param1', 'param2' itd. Parametry pozwalają na realizację 100 wiadomości w jednym żądaniu, co pozwoli na wysyłkę SMS do np. 100k odbiorców poprzez 1000 żądań POST.

    **W sytuacji przekroczenia ilości 30 żądań (3000 SMS) / min, system może zacząć buforować żądania i przetwarzać je w osobnej kolejce. Więcej o buforowaniu [tutaj](_doc_slate_index.html.md#bufor).**

4.  Niezależnie od tego jakiego rodzaju żądania wysyłasz, należy zaimplementować mechanizm ponawiania wysyłki w przypadku odpowiedzi od API innej niż prawidłowa ('200 OK' wraz z nadanym przez nas ID wysyłki 'messageId'). Dobrą praktyką jest ponawianie wysłania żądania po jakimś odstępie czasowym, np. 5 sekund, który to czas wzrasta wraz z każdą ponowną próbą (nie więcej niż np. 10 minut).
5.  Szczegóły dotyczące sposobu wysyłania żądań są opisane [tutaj](_doc_slate_index.html.md#wyslanie-sms-metoda-post-zalecane).

## Rozpoczęcie współpracy

Aby zacząć korzystać z platformy należy założyć konto w serwisie SMSPLANET pod adresem [https://panel.smsplanet.pl/register](https://panel.smsplanet.pl/register). Następnie należy uzupełnić dane firmy w zakładce 'Mój Profil' oraz doładować konto punktami (PrePaid) lub podpisać umowę abonamentową (PostPaid) co umożliwi wysyłkę wiadomości.

## Autoryzacja
```
Przykład:
curl -X POST \
https://api2.smsplanet.pl/sms \
-H 'Authorization: Bearer QwErTyUiOpaSdFgHjKlZxCvBnm12345' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'from=TEST&to=500111222&msg=wiadomość'
```
Dostepne są dwie metody autoryzacji żądań:

**1\. Tokeny API (zalecane)**

Zalecamy autoryzację żądań do API przy pomocy [Tokenów API](https://panel.smsplanet.pl/s/api?tab=tab4). Token można wygenerować w panelu klienta. Token należy dodać do każdego wysyłanego żądania w nagłówku autoryzacyjnym "Authorization".

#### Authorization: Bearer <token>

**2\. Klucz i hasło API**

Dostępna jest również metoda autoryzacji za pomocą klucza API i hasła API przekazywanych jako parametry w żądaniu. Aby skorzystać z tej metody, należy nadać hasło do API w [panelu klienta](https://panel.smsplanet.pl/s/api?tab=tab2).

## Filtracja adresów IP

Aby dodatkowo zabezpieczyć komunikację z naszym SMS API, można ustalić listę zaufanych adresów IP. Tylko połączenia z tej listy będą akceptowane. Filtracja adresów IP dotyczy tylko wysyłek realizowanych poprzez API. Filtracja nie dotyczy wysyłek realizowanych z poziomu panelu WWW.

Filtr można zdefiniować w panelu klienta po zalogowaniu pod adresem [https://panel.smsplanet.pl/s/api](https://panel.smsplanet.pl/s/api)

## Dostępne metody

## Wysłanie SMS metodą GET
```
`curl -X GET -G \ 'https://api2.smsplanet.pl/sms' \ -d key=klucz \ -d password=haslo \ -d from=TEST \ -d to=600111222 \ -d msg=Wiadomosc`
```
```
`<?php $url = "https://api2.smsplanet.pl/sms"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'from' => 'TEST', 	'to' => '600111222', 	'msg' => 'Wiadomosc testowa' ]; $response=send_get($url, $params); var_dump($response); function send_get($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url . '?'.$params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"messageId":"191919"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`GET https://api2.smsplanet.pl/sms`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| from | true | string | Widoczna przez odbiorców nazwa nadawcy SMS. Można korzystać z testowej nazwy 'TEST' lub z nazw zgłoszonych poprzez panel klienta (zakładka 'Pole nadawcy') i zaakceptowanych przez administrację serwisu. W przypadku komunikacji dwukierunkowej (2WAY), należy podać specjalny numer telefonu dedykowany do komunikacji dwustronnej |
| msg | true | string | Treść wiadomości. Pojedynczy SMS może mieć długość 160 znaków lub 70 znaków jeśli w wiadomości występuje przynajmniej jeden znak specjalny (w tym polskie znaki). Jeśli treść wiadomości jest dłuższa zostanie podzielona na kilka SMS (max. 6) |
| to | true | multi string array | Numer odbiorcy wiadomości. Dozwolone formaty \[600111222, 48600111222, +48600111222\]. Element ten może występować wielokrotnie, co spowoduje wysłanie danej wiadomości do wielu odbiorców na raz. Ze względu na ograniczenia metody GET (max. ok. 2000 znaków), korzystanie z tej metody nie jest zalecane dla wysyłek powyżej 200 numerów. Nieprawidłowe numery zostaną pominięte. Jeśli numer występuje 2 lub więcej razy duplikaty zostaną pominięte |
| date | false | string | Data określająca kiedy wiadomość ma być wysłana. Brak daty lub data przeszła spowodują natychmiastowe wysłanie wiadomości. Dozwolone formaty \[Unixtime (np. 1276623871), dd-MM-yyyy HH:mm:ss (np. 21-05-2017 10:05:00)\] Wysyłki są planowane wg polskiej strefy czasowej |
| name | false | string | Nazwa wysyłki. Nadanie nazwy wysyłce, może ułatwić jej późniejsze odnalezienie w historii. |
| clear\_polish | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1 to wszystkie polskie znaki w treści wiadomości zostaną zastąpione na swoje odpowiedniki, np. ą=a, ć=c, ł=l, itd. Wartość domyślna: 0. |
| test | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1, wiadomość nie zostanie wysłana. Zwrócona zostanie jednak standardowa odpowiedź API. Służy celom testowym. Wartość domyślna: 0. |
| company\_id | false | string | Dodatkowe pole określające firmę, która wysyła żądanie. Stosowane do systemu poleceń (ref). |
| transactional | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1, zostanie podjęta próba wysłania wiadomości kanałem transakcyjnym. Kanał transakcyjny służy jedynie do wysyłania wiadomości o charakterze jednorazowym, niemarketingowym (np. kod PIN do logowania). Kanał transakcyjny jest dostępny jedynie po akceptacji przez administrację serwisu. Wartość domyślna: 0. |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| messageId | Unikalny identyfikator wysyłki nadany przez smsplanet. Może zostać wykorzystany np. do anulowania zaplanowanej wysyłki lub pobrania informacji o wysyłce.
**Ważne! ([Bufor kolejkowy](_doc_slate_index.html.md#zalecenia_limity))** Jeśli messageId zaczyną się od ciągu "B-" (np."B-5-123456789"), oznacza to, że wiadomość trafiła do bufora kolejkowego i zostanie wysłana z opóźnieniem (od 10 do 30 sekund). Zwrócony identyfikator można wykorzystać jedynie do pobrania [informacji o wysyłkach](_doc_slate_index.html.md#pobranie-szczegolowych-danych-wysylki). |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Wysłanie SMS metodą POST (zalecane)
```
`curl -X POST \ 'https://api2.smsplanet.pl/sms' \ -d key=klucz \ -d password=haslo \ -d from=TEST \ -d to=600111222 \ -d msg=Wiadomosc`
```
```
`<?php $url = "https://api2.smsplanet.pl/sms"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'from' => 'TEST', 	'to' => '600111222', 	'msg' => 'Wiadomosc testowa' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
Przykład dla wielu numerów:
`<?php $url = "https://api2.smsplanet.pl/sms"; $params = array( 	'key' => 'KLUCZ_API', 	'password' => 'HASLO_API', 	'from' => 'TEST', 	'msg' => 'Wiadomosc testowa' ); $to = array('600111222', '700333444'); $params_string = http_build_query($params); foreach ($to as $msisdn) { 	$params_string = $params_string . '&to=' . $msisdn; } $response=send_post($url, $params_string); var_dump($response); function send_post($url,$params_string) { 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"messageId":"191919"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Zalecenia i limity

[Kliknij tutaj, aby przeczytać o zaleceniach i limitach dotyczących wysyłania SMS](_doc_slate_index.html.md#zalecenia_limity)

### Adres URL

`POST https://api2.smsplanet.pl/sms`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| from | true | string | Widoczna przez odbiorców nazwa nadawcy SMS. Można korzystać z testowej nazwy 'TEST' lub z nazw zgłoszonych poprzez panel klienta (zakładka 'Pole nadawcy') i zaakceptowanych przez administrację serwisu. W przypadku komunikacji dwukierunkowej (2WAY), należy podać specjalny numer telefonu dedykowany do komunikacji dwustronnej |
| msg | true | string | Treść wiadomości. Pojedynczy SMS może mieć długość 160 znaków lub 70 znaków jeśli w wiadomości występuje przynajmniej jeden znak specjalny (w tym polskie znaki). Jeśli treść wiadomości jest dłuższa zostanie podzielona na kilka SMS (max. 6) |
| to | true | multi string array | Numer odbiorcy wiadomości. Dozwolone formaty \[600111222, 48600111222, +48600111222\]. Element ten może występować wielokrotnie co spowoduje wysłanie danej wiadomości do wielu odbiorców na raz. Maksymalna ilość odbiorców w jednym żądaniu wynosi 10000. Nieprawidłowe numery zostaną pominięte. Jeśli numer występuje 2 lub więcej razy duplikaty zostaną pominięte |
| date | false | string | Data określająca kiedy wiadomość ma być wysłana. Brak daty lub data przeszła spowodują natychmiastowe wysłanie wiadomości. Dozwolone formaty \[Unixtime (np. 1276623871), dd-MM-yyyy HH:mm:ss (np. 21-05-2017 10:05:00)\] Wysyłki są planowane wg polskiej strefy czasowej |
| name | false | string | Nazwa wysyłki. Nadanie nazwy wysyłce, może ułatwić jej późniejsze odnalezienie w historii. |
| clear\_polish | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1 to wszystkie polskie znaki w treści wiadomości zostaną zastąpione na swoje odpowiedniki, np. ą=a, ć=c, ł=l, itd. Wartość domyślna: 0. |
| param1
param2
param3
param4 | false | string | Parametry pozwalają na wysłanie do 100 spersonalizowanych wiadomości przy wykorzystaniu pojedynczego wywołania API. W jednej wiadomości można zastosować maksymalnie 4 parametry.
Wartości tych parametrów zostaną wstawione w treść wiadomości - w miejscach, które zostaną zdefiniowane jako **\[%parametr1%\], \[%parametr2%\], \[%parametr3%\], \[%parametr4%\]**.
Wartości parametrów muszą być oddzielone od siebie znakiem pipe \`|\`, np.
**param1=Jan|Zbigniew|Jerzy***param2=Kowalski|Nowak|Wiśniewski**

Ilość wartości występujących w poszczególnych parametrach musi być dokładnie taka sama jak ilość numerów odbiorczych (_parametr "to"_). W przeciwnym przypadku zwrócony zostanie komunikat błędu.

 |
| test | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1, wiadomość nie zostanie wysłana. Zwrócona zostanie jednak standardowa odpowiedź API. Służy celom testowym. Wartość domyślna: 0. |
| company\_id | false | string | Dodatkowe pole określające firmę, która wysyła żądanie. Stosowane do systemu poleceń (ref). |
| transactional | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1, zostanie podjęta próba wysłania wiadomości kanałem transakcyjnym. Kanał transakcyjny służy jedynie do wysyłania wiadomości o charakterze jednorazowym, niemarketingowym (np. kod PIN do logowania). Kanał transakcyjny jest dostępny jedynie po akceptacji przez administrację serwisu. Wartość domyślna: 0. |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| messageId | Unikalny identyfikator wysyłki nadany przez smsplanet. Może zostać wykorzystany np. do anulowania zaplanowanej wysyłki lub pobrania informacji o wysyłce.
**Ważne! ([Bufor kolejkowy](_doc_slate_index.html.md#zalecenia_limity))** Jeśli messageId zaczyna się od ciągu "B-" (np."B-5-123456789"), oznacza to, że wiadomość trafiła do bufora kolejkowego i zostanie wysłana z opóźnieniem (od 10 do 30 sekund). Zwrócony identyfikator można wykorzystać jedynie do pobrania [informacji o wysyłkach](_doc_slate_index.html.md#pobranie-szczegolowych-danych-wysylki). |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Wysłanie MMS
```
`curl -X POST \ 'https://api2.smsplanet.pl/mms' \ -d key=klucz \ -d password=haslo \ -d from=48664079876 \ -d to=600111222 \ -d subject=Temat \ -d attachment=https://link.do/zdjecia/kotka.jpg \ -d msg=Treść`
```
```
`<?php $url = "https://api2.smsplanet.pl/mms"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'from' => 'TEST', 	'to' => '600111222', 	'subject' => 'temat', 	'attachment' => 'https://link.do/zdjecia/kotka.jpg', 	'msg' => 'Wiadomość testowa' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"messageId":"191919"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/mms`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| from | true | string | Numer telefonu nadawcy MMS. Nasz aktualny numer do obsługi MMS jest dostępny w panelu klienta po zalogowaniu. |
| subject | true | string | Temat wiadomości. Zalecamy jego podanie ponieważ, niektóre modele telefonów mogą nie przyjmować MMS bez podanego tematu. |
| msg | true | string | Treść wiadomości. Całkowity rozmiar MMS (wiadomość + załącznik + temat) nie może przekroczyć 300kB. |
| attachment | true | string | Adres url załącznika MMS lub obraz w formacie Base64. Należy podać pełny adres url lub obraz w formacie Base64. Całkowity rozmiar MMS (wiadomość + załącznik + temat) nie może przekroczyć 300kB. |
| to | true | multi string array | Numer odbiorcy wiadomości. Dozwolone formaty \[600111222, 48600111222, +48600111222\] Element ten może występować wielokrotnie co spowoduje wysłanie danej wiadomości do wielu odbiorców na raz Maksymalna ilość odbiorców w jednym żądaniu wynosi 10000. Nieprawidłowe numery zostaną pominięte. Jeśli numer występuje 2 lub więcej razy duplikaty zostaną pominięte |
| date | false | string | Data określająca kiedy wiadomość ma być wysłana. Brak daty lub data przeszła spowodują natychmiastowe wysłanie wiadomości. Dozwolone formaty \[Unixtime (np. 1276623871), dd-MM-yyyy HH:mm:ss (np. 21-05-2017 10:05:00)\] Wysyłki są planowane wg polskiej strefy czasowej |
| clear\_polish | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1 to wszystkie polskie znaki w treści wiadomości zostaną zastąpione na swoje odpowiedniki, np. ą=a, ć=c, ł=l, itd. |
| test | false | enum (0, 1) | Jeśli wartość tego parametru wynosi 1, wiadomość nie zostanie wysłana. Zwrócona zostanie jednak standardowa odpowiedź API. Służy celom testowym. |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| messageId | Unikalny identyfikator wysyłki nadany przez smsplanet. Może zostać wykorzystany np. do anulowania zaplanowanej wysyłki lub pobrania jej statusu.
**Ważne! ([Bufor kolejkowy](_doc_slate_index.html.md#zalecenia_limity))** Jeśli messageId zaczyna się od ciągu "B-" (np."B-5-123456789"), oznacza to, że wiadomość trafiła do bufora kolejkowego i zostanie wysłana z opóźnieniem (od 10 do 30 sekund). Zwrócony identyfikator można wykorzystać jedynie do pobrania [informacji o wysyłkach](_doc_slate_index.html.md#pobranie-szczegolowych-danych-wysylki). |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Anulowanie zaplanowanej wysyłki
```
`curl -X POST \ 'https://api2.smsplanet.pl/cancelMessage' \ -d key=klucz \ -d password=haslo \ -d messageId=123456 \`
```
```
`<?php $url = "https://api2.smsplanet.pl/cancelMessage"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'messageId' => '123456' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/cancelMessage`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| messageId | true | integer | Unikalny identyfikator wysyłki (nie może być to [identyfikator bufora](_doc_slate_index.html.md#bufor)) |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Generowanie raportu zbiorczego
```
`curl -X POST \ 'https://api2.smsplanet.pl/generateReport' \ -d key=klucz \ -d password=haslo \ -d from=01-05-2019 \ -d to=30-06-2019`
```
```
`<?php $url = "https://api2.smsplanet.pl/generateReport"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'from' => '01-05-2019', 	'to' => '30-06-2019' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK",
"message":
  "ID;Identyfikator użytkownika;Data utworzenia;Data wysyłki;Nadawca;Treść;Wiadomości;Dostarczone;Koszt;Zwroty   1;788;21-05-2018 17:05:12;21-05-2018 17:15:00;TEST;Testowa wysyłka SMS;1;1;1;0   2;788;22-06-2018 18:06:13;22-06-2018 18:16:00;TEST;Kolejna wysyłka;1;1;1;0"
}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/generateReport`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| from | true | string | Data od w formacie dd-mm-yyyy HH:MM:ss (np. 01-05-2017 00:00:00) |
| to | true | string | Data do w formacie dd-mm-yyyy HH:MM:ss (np. 30-06-2017 23:59:59) |
| detailed | false | boolean | true/false - definiuje czy raport ma zawierać szczegółowe informacje o każdej wysyłce (numery telefonów wraz ze statusami doręczeń). Wartość domyślna: false |
| responseType | false | string | "json" lub "csv". Wartość domyślna: "json" |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |
| message | Treść raportu w formacie CSV (średnik jako separator) |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Pobranie szczegółowych danych wysyłki
```
`curl -X POST \ 'https://api2.smsplanet.pl/getMessageInfo' \ -d key=klucz \ -d password=haslo \ -d messageId=123456 \`
```
```
`<?php $url = "https://api2.smsplanet.pl/getMessageInfo"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'messageId' => '123456' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK",
"message":
Pole nadawcy: TEST
Nazwa wysyłki:
Treść wiadomości: wiadomość testowa
Data wysyłki: 22-12-2019 17:46:34
Wysłane: 3
Dostarczone: 3
Zwroty: 0
"Numer telefonu";"Dostarczono";"Data dostarczenia";"Powód odrzucenia";"Pobrano opłatę"
"000111222";"TAK";"22-12-2019 17:46:40";"";"TAK"
"333444555";"TAK";"22-12-2019 17:46:40";"";"TAK"
"666777888";"TAK";"22-12-2019 17:46:40";"";"TAK"
}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/getMessageInfo`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| messageId | true | multi integer array | Unikalny identyfikator wysyłki - parametr ten może występować wiele razy, spowoduje to pobranie szczegółów wielu wysyłek na raz. Maksymalnie można podać do 1000 parametrów messageId w pojedynczym żądaniu. |
| responseType | false | string | "json" lub "csv". Wartość domyślna: "json" |

### Limity

|  |  |
| --- | --- |
| Metoda nie może być wywoływana częściej niż raz na 3 minuty. Statusy doręczeń aktualizowane są co kilka minut w związku z czym częstsze wywoływanie metody jest bezpodstawne. |  |
|  |  |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |
| message | Treść raportu w formacie CSV (średnik jako separator). Pierwsze 7 linii zawiera informacje o wysyłce. W kolejnych liniach znajdują się szczegóły doręczeń na każdy z numerów. |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Webhooki

Webhooki umożliwiają otrzymywanie powiadomień o zdarzeniach, które wystąpiły w systemie. Takim zdarzeniem może być np. doręczenie SMS'a. Po utworzeniu webooka, nasz system wyśle żądanie typu POST na adres URL wskazany podczas tworzenia webhooka. W ciele żądania (body) przesłane zostanią informacje dotyczące danego zdarzenia w formacie JSON.

### Przykładowe powiadomienie

##### MESSAGE\_NOTIFICATION\_WEBHOOK

   `{        "notification": {         "deliveryError": ""         "sentDate": "24-05-2024 11:45:24",         "parts": "1",         "messageId": "1234567",         "from": "AUTO HANDEL",         "delivered": "true",         "to": "600700800",         "deliveryDate": "24-05-2024 11:45:30",        }      }`

Nasz system oczekuje w odpowiedzi kodu HTTP 200. W przypadku otrzymania innego kodu odpowiedzi, system będzie ponawiał wysyłkę powiadomienia w różnych odstępach czasowych łącznie przez ok. 16 godzin. Po upływie tego czasu powiadomienie zostanie uznane za dostarczone.

**Ważne!** Po 500 nieudanych próbach doręczenia powiadomienia, następujących bezpośrednio po sobie, webhook zostanie uznany za nieprawidłowy i automatycznie usunięty.

### Nagłówek podpisu

W celu zapewnienia integralności i bezpieczeństwa przesyłanych danych, w wysyłanych powiadomieniach znajduje się dodatkowy nagłówek: '**Signature**', który może zostać zweryfikowany w otrzymanych żądaniach.

Podpis jest obliczany na podstawie całej, surowej zawartości żądania (body), przy użyciu algorytmu HMAC SHA256. Binarny wynik funkcj haszującej jest następnie kodowany w Base64. Po podpisu wykorzytywany jest indywidualny dla każdego użytkownika klucz (Signature Key), który można znaleźć w panelu klienta w sekcji **API -> Webhooki**.

Przykład:

Zawartość żądania (body):
`{"notification":{"deliveryError":"","sentDate":"24-05-2024 11:45:24","parts":"1","messageId":"1234567","from":"AUTO HANDEL","delivered":"true","to":"600700800","deliveryDate":"24-05-2024 11:45:30"}}`

Klucz podpisu (Signature key):
`3e13a3d9d531cdb791b96b01b733f27c`

Dla takich danych prawidłowy podpis to: `Upe2XxZCyeQyqADt0RuQ4l8RtWgjaSlKzyB7ogGjs4g=`
Uwaga: jeśli dla danych z powyższego przykładu otrzymujesz inną wartość podpisu, upewnij się, że dane JSON są sformatowane dokładnie w ten sam sposób w jaki są prezentowane powyżej (bez białych znaków). Pamiętaj również, aby po otrzymaniu wyniku funkcji haszującej, zakodować go w postać Base64.

## Webhook - tworzenie

Metoda ta pozwala na utworzenie webhook'a. Możliwe jest dodanie tylko jednego webhooka danego typu.
```
`curl -X POST \ 'https://api2.smsplanet.pl/webhooks/create' \ -d key=klucz \ -d password=haslo \ -d url=http://mojastrona.pl/webhook \ -d type=MESSAGE_NOTIFICATION_WEBHOOK \`
```
```
`<?php $url = "https://api2.smsplanet.pl/webhooks/create"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'url' => 'http://mojastrona.pl/webhook', 	'type' => 'MESSAGE_NOTIFICATION_WEBHOOK' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
### Adres URL

`POST https://api2.smsplanet.pl/webhooks/create`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| url | true | string | Adres URL na który będą przekazywane powiadomienia |
| type | true | enum | Typ webhooka. Dopuszczalne wartości to:
**MESSAGE\_NOTIFICATION\_WEBHOOK** - powiadomienia o statusie wysłanych wiadomości

 |

### Odpowiedź:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Webhook - usuwanie

Metoda ta pozwala na usunięcie webhook'a.
```
`curl -X POST  \ 'https://api2.smsplanet.pl/webhooks/remove' \ -d key=klucz \ -d password=haslo \ -d type=MESSAGE_NOTIFICATION_WEBHOOK \`
```
```
`<?php $url = "https://api2.smsplanet.pl/webhooks/remove"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'type' => 'MESSAGE_NOTIFICATION_WEBHOOK' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
### Adres URL

`POST https://api2.smsplanet.pl/webhooks/remove`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| type | true | enum | Typ webhooka. Dopuszczalne wartości to:
**MESSAGE\_NOTIFICATION\_WEBHOOK** - powiadomienia o statusie wysłanych wiadomości

 |

### Odpowiedź:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Webhook - lista

Metoda ta pozwala na pobranie listy wszystkich utworzonych webhook'ów.
```
`curl -X GET -G \ 'https://api2.smsplanet.pl/webhooks/list' \ -d key=klucz \ -d password=haslo \`
```
```
`<?php $url = "https://api2.smsplanet.pl/webhooks/list"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', ]; $response=send_get($url, $params); function send_get($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url . '?'.$params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"webhooks":[{ "type": "MESSAGE_NOTIFICATION_WEBHOOK", "url": "https://link.do/webhook"}]}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`GET https://api2.smsplanet.pl/webhooks/list`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| webhooks | Lista wszystkich utworzonych webhook'ów |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Zgłoszenie pola nadawcy
```
`curl -X POST  \ 'https://api2.smsplanet.pl/addSenderField' \ -d key=klucz \ -d password=haslo \ -d senderField=MOJA FIRMA \`
```
```
`<?php $url = "https://api2.smsplanet.pl/addSenderField"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'senderField' => 'MOJA FIRMA' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/addSenderField`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| senderField | true | string | Nazwa pola nadawcy - max. 11 znaków. Dopuszczalne znaki: a-z A-Z 0-9 . - + \_ ! \[spacja\] (numer telefonu nie jest dozwolony) |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Pobranie listy dostępnych pól nadawcy
```
`curl -X POST  \ 'https://api2.smsplanet.pl/getSenderFields' \ -d key=klucz \ -d password=haslo \ -d product=SMS \`
```
```
`<?php $url = "https://api2.smsplanet.pl/getSenderFields"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'product' => 'SMS' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"senderFields":"TEST,Informacja,Sklep,MojaFirma"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/getSenderFields`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| product | false | enum (SMS, 2WAY, MMS) | Nazwa produktu dla którego sprawdzane są pola nadawcy. Wartość domyślna: SMS |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| senderFields | Dostępne pola nadawcy oddzielone przecinkami |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Dodanie numeru do czarnej listy
```
`curl -X POST  \ 'https://api2.smsplanet.pl/blacklist/add' \ -d key=klucz \ -d password=haslo \ -d msisdn=600111222 \`
```
```
`<?php $url = "https://api2.smsplanet.pl/blacklist/add"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'msisdn' => '600111222' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/blacklist/add`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| msisdn | true | string | Numer telefonu |
| validTo | false | string | Data ważności w formacie dd-mm-yyyy (np. 15-09-2025) |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Usunięcie numeru z czarnej listy
```
`curl -X POST  \ 'https://api2.smsplanet.pl/blacklist/remove' \ -d key=klucz \ -d password=haslo \ -d msisdn=600111222 \`
```
```
`<?php $url = "https://api2.smsplanet.pl/blacklist/remove"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'msisdn' => '600111222' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/blacklist/remove`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| msisdn | true | string | Numer telefonu |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Skracanie linków
```
`curl -X POST  \ 'https://api2.smsplanet.pl/shortUrl' \ -d key=klucz \ -d password=haslo \ -d longUrl=https://google.com \`
```
```
`<?php $url = "https://api2.smsplanet.pl/shortUrl"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'longUrl' => 'https://google.com' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"shortUrl":"https://link.do/Qdwjg"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/shortUrl`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| longUrl | true | string | Pełny adres URL, który chcemy skrócić |
| customAlias | false | string | Własny (proponowany) alias dla skróconego linku. Jeśli alias nie będzie zajęty, zostanie użyty w skróconym linku. Domyślnie alias to losowy ciąg znaków. |
| save | false | boolean | Podanie wartości 'true' spowoduje zapisanie linku w panelu klienta. Wartość domyślna: 'false'. |
| domain | false | string | Domena skróconego linku. Wartość domyślna: wejdz.do. Dozwolone wartości: wejdz.do, link.do |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| shortUrl | Wygenerowany skrócony link |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Lista skróconych linków
```
`curl -X GET -G \ 'https://api2.smsplanet.pl/shortener/list' \ -d key=klucz \ -d password=haslo \`
```
```
`<?php $url = "https://api2.smsplanet.pl/shortener/list"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"links":[{ "date": "27-04-2021 14:24:27", "shortURL": "https://link.do/iyv5w", "clicks": "0", "longURL": "https://smsplanet.pl/api"}]}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`GET https://api2.smsplanet.pl/shortener/list`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| shortUrl | false | string | Skrócony adres URL. Brak parametru spowoduje pobranie informacji o wszystkich linkach. |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| links | Lista informacji o skróconych linkach |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Usuwanie skróconych linków
```
`curl -X POST  \ 'https://api2.smsplanet.pl/shortener/remove' \ -d key=klucz \ -d password=haslo \ -d alias=XYZ \`
```
```
`<?php $url = "https://api2.smsplanet.pl/shortener/remove"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'alias' => 'XYZ' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"result":"OK"}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/shortener/remove`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| alias | true | multi string array | Alias linku lub cały skrócony link. Element ten może występować wielokrotnie w celu usunięcia wielu elementów na raz. |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| result | Pole może przyjąć tylko wartość "OK" |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Sprawdzenie stanu konta (tylko PrePaid)
```
`curl -X POST  \ 'https://api2.smsplanet.pl/getBalance' \ -d key=klucz \ -d password=haslo`
```
```
`<?php $url = "https://api2.smsplanet.pl/getBalance"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo' ]; $response=send_post($url, $params); var_dump($response); function send_post($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url); 	curl_setopt($ch,CURLOPT_POST, true); 	curl_setopt($ch,CURLOPT_POSTFIELDS, $params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
{"balance":251}
```
> lub
```
{"errorMsg":"Niepoprawny klucz - sprawdź swój klucz API.","errorCode":101}
```
### Adres URL

`POST https://api2.smsplanet.pl/getBalance`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |

### Odpowiedź w przypadku powodzenia:

| Parametr | Opis |
| --- | --- |
| balance | Ilość punktów na koncie PrePaid |

### Odpowiedź w przypadku niepowodzenia:

| Parametr | Opis |
| --- | --- |
| errorMsg | Treść informująca o przyczynie błędu |
| errorCode | Unikalny kod błędu |

## Liczenie długości SMS

Metoda pozwala na sprawdzenie, na jaką ilość SMSów zostanie podzielona nasza wiadomość. Maksymalna długość pojedynczej wiadomości wynosi 6 części (6 SMS).
```
`curl -X GET -G \ 'https://api2.smsplanet.pl/sms/parts-count' \ -d key=klucz \ -d password=haslo \ -d content=treść SMSa do sprawdzenia \`
```
```
`<?php $url = "https://api2.smsplanet.pl/sms/parts-count"; $params = [ 	'key' => 'klucz_api', 	'password' => 'haslo', 	'content' => 'treść SMSa do sprawdzenia' ]; $response=send_get($url, $params); function send_get($url,$params) { 	$params_string = http_build_query($params); 	$ch = curl_init(); 	curl_setopt($ch,CURLOPT_URL, $url . '?'.$params_string); 	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0); 	$response = curl_exec($ch); 	curl_close ($ch);  	return $response; } ?>`
```
> Przykładowa odpowiedź:
```
3
```
### Adres URL

`GET https://api2.smsplanet.pl/sms/parts-count`

### Lista parametrów

| Parametr | Wymagany | Typ | Opis |
| --- | --- | --- | --- |
| key | false | string | Klucz API identyfikujący użytkownika. Wymagany tylko w przypadku braku tokena autoryzacyjnego |
| password | false | string | Hasło do API. Domyślnie wyłączone. Pierwsze hasło należy nadać w panelu klienta |
| content | true | string | Treść wiadomości, dla której chcemy sprawdzić na jaką ilość części zostanie podzielona |

### Odpowiedź:

|  |
| --- |
| Zawsze zwracana jest liczba (integer) podająca ilość części SMS |

## Odbieranie SMS

Platforma umożliwia skonfigurowanie przekierowania wiadomości SMS, które otrzymaliśmy z numeru dwukierunkowego (2WAY). Wszystkie odebrane wiadomości trafiają do panelu klienta, również po przekierowaniu. Przekierowanie może odbywać się na 3 sposoby:

*   przekierowanie na numer telefonu
*   przekierowanie na adres email
*   przekierowanie na adres URL

### Przekierowanie należy skonfigurować w panelu klienta:

[https://panel.smsplanet.pl/s/receive/settings](https://panel.smsplanet.pl/s/receive/settings)

`Menu: "Odbieranie wiadomości" -> "Ustawienia"`

## Kody błędów API

Lista błędów zwracanych przez API wraz z kodami

| Kod | Opis |
| --- | --- |
| 100 | Błąd parsowania danych - sprawdź czy wysyłasz poprawne dane. |
| 101 | Niepoprawny klucz - sprawdź swój klucz API. |
| 102 | Niepoprawne hasło API. Upewnij się, że wysyłasz poprawne hasło. |
| 103 | Niepoprawne pole nadawcy. |
| 104 | Wiadomość jest zbyt długa. Limit wynosi 6 sms na wiadomość. |
| 105 | Wykorzystano ustawiony limit na wysyłki. |
| 106 | Lista odbiorców jest pusta. Upewnij się, że wprowadzono przynajmniej jeden numer nie znajdujący się na czarnej liście. |
| 108 | Data \[%s\] jest niepoprawna. Dozwolony format daty opisany jest w specyfikacji. |
| 109 | Brak wystarczających środków na koncie. |
| 110 | Adres IP \[%s\] nie znajduje się na liście dozwolonych adresów. |
| 111 | Limit ilości odbiorców wynosi 10000. |
| 113 | Niepoprawne pole nadawcy '%s' dla produktu innego niż MMS. |
| 114 | Wiadomość MMS może zawierać tylko jeden załącznik. |
| 115 | Rozmiar wiadomości przekracza %s kB. |
| 200 | Nie znaleziono użytkownika. Sprawdź dane autoryzacyjne. |
| 201 | Nieprawidłowy token API. Sprawdź czy token jest prawidłowo wysyłany. |
| 202 | Token API jest nieaktywny. Możesz go aktywować w panelu klienta. |
| 203 | Token API wygasł. Sprawdź datę ważności. |

## Statusy doręczeń SMS

W przypadku braku poprawnego dostarczenia wiadomości, w raporcie wysyłki będzie można odznaleźć status błędu z tym związany.

Pełna lista błędnych statusów doręczeń SMS:

| Numer | Status |
| --- | --- |
| 1 | Wstępnie odrzucony |
| 2 | Nieprawidłowy operator |
| 3 | Brak kanału do wysłania SMS |
| 4 | Niedozwolona treść SMS - wulgaryzmy |
| 5 | Niedozwolona treść SMS - Premium |
| 6 | Niedozwolona treść Nadpisu |
| 7 | Wygasł |
| 8 | Skasowany |
| 9 | Niedostarczony |
| 10 | Nieznany błąd |
| 11 | Odrzucony |

