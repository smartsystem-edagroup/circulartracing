# Circular Tracing Gateway IIoT
Circular Tracing ha come scopo la realizzazione di un sistema misto hardware e software per la tracciabilità avanzata di componenti, semilavorati, e materie prime per l’industria manifatturiera durante l’intero ciclo di vita del prodotto altamente innovativo. Questa repository contiene gli sviluppi relativi al Gateway IIoT di Circular Tracing. Per l'esecuzione del codice è necessario utilizzare l'hardware proprietario VAR-SOM-MX7 di Meridionale Impianti, partner del progetto Circular Tracing. Per la connessione diretta al Gateway IIoT, contattare direttamente gli sviluppatori della repository.

# Organizzazione cartelle
  - Producers: cartella contente i file che simulano il comportamento dei sensori. Scrivono sul broker MQTT interno utilizzando SenML e contengono lo script per connettersi in modo sicuro (ossia certificati + autenticazione) al broker
  - Interface: legge i dati dal broker interno, li elabora e li manda su un broker esterno (per testare in questo momento viene utilizzato un broker che ha come domain test.mosquitto.org). Prendendo gli script in Consumers, si può mandare anche sul broker interno, ovviamente cambiando gli user, descritti in sezioni successive
  - Consumers: legge i dati che arrivano dalle Interface semplicemente. Fanno la subscribe su un broker esterno, ma prendendo gli esempi da Producers e da Interface, si possono facilmente adattare.
  - Configuration: file di configurazione per replicare il broker su altri dispositivi, spiegato in dettaglio nelle sezioni seguenti
  - Certificates: cartella contentente i certificati per connettersi al broker del gateway, spiegato in dettaglio nelle sezioni seguenti

# Note importanti
- Tutti i file vanno runnati con python3: paho mqtt ha un modo strano di mandare i messaggi con python2, nel senso che accetta solo stringhe, perciò c'è bisogno di fare tutto con python3

- Paho MQTT non supporta TLS 1.3, il broker è configurato per il supporto anche di TLS 1.2, ma potrebbe dare problemi. In caso sia questo il caso, prego di inviare una mail a franco.volante@polito.it segnalando l'errore, così che possa essere corretto.ù

# Come connettersi al broker del gateway
Il broker interno ha una doppia autenticazione:

- Certificati: per questi c'è bisogno di certificati generati internamente dalla board. Nella cartella Certificates sono disponibili i 3 certificati che servono per connettersi, spiegati meglio nella sotto sezione successiva
- Username e Password: in questo momento ci sono tre utenti con le rispettive password, descritte in dettaglio nelle prossime sotto sezioni

## Certificati
La cartella Certificates contiene 2 certificati ed una chiave, necessari per connettersi al broker MQTT interno:

 - client.crt: certificato del client rilasciato dalla Certificate Authority interna del Gateway: è il certificato del dispositivo che si sta connettendo. Per ragioni di sviluppo c'è un certificato unico per tutti i client. In seguito verrà rilasciato un certificato per dispositivo.
 - client.key: la chiave che va in coppia con client.crt
 - ca.crt: il certificato della Certificate Authority interna al gateway. Serve a verificare la correttezza del certificato inviato dal broker per autenticarsi

Questi tre file sono necessari per connettersi sia come publisher che come subscriber. In particolar modo, il loro percorso ASSOLUTO (non relativo) va inserito come parametro nella funzione:
client.tls_set(ca_certs=\<path assoluto del file ca.crt>, certfile=\<path assoluto del file client.crt>, keyfile=\<path assoluto del file client.key>).

## Username e password
In questo momento, ci sono solo tre utenti autorizzati ad accedere. Username e Password di questi utenti coincidono.

- sensor : può scrivere sui topic "image/#" e "sensor/#"
- gateway : può leggere sui topic "image/#" e "sensor/#" e scrivere su "output/#"
- listener :  può leggere sui topic "output/#"

# Come replicare il broker su un altra board
Il broker può essere replicato utilizzando i file contenuti nella cartella Configuration. Utilizzando mosquitto, vanno inseriti nella cartella di configurazione mosquitto (che per i sistemi Linux è in /etc/mosquitto/, per gli altri OS non è stato considerato).
L'unica cosa che manca sono i certificati, per i quali non possono essere usati quelli salvati nella cartella Certificates, in quanto c'è bisogno di altre chiavi e certificati che non distribuisco in questa cartella in quanto sono privati e interni al gateway.
Tuttavia, la loro generazione viene effettuato seguendo la documentazione di mosquitto-tls, consultabile qui: https://mosquitto.org/man/mosquitto-tls-7.html
Infine, il luogo dove salvarli e come finire di configurare il tutto è disponibile in questa guida online, in particolare gli step 7 e 8: http://www.steves-internet-guide.com/mosquitto-tls/

Per eventuali problemi, errori o chiarimenti, mandare una mail a luca.barbierato@polito.it
