# IOT - Serrure connectée

Projet réalisé dans le cadre d'un cours d'IOT en deuxième année d'école informatique.    
Réalisation d'une serrure connecté ouvrable par un lecteur de badge RFID. La serrure est associée à une interface web et à une API.

## Fonctionnalités

Après avoir conceptualisé une serrure en 3D, nous avons utilisé une **Raspberry Pi Zero**,  un lecteur de badge **RFID**, un **Servo**, et deux LEDS pour confectionner notre serrure.

#### La serrure 

Lorsque l'on passe le badge devant la serrure, celle-ci interroge l'**API** qui vérifie que ce badge est autorisé à ouvrir la serrure. Si c'est le cas, elle s'ouvre durant 5s et la LED verte s'allume. Sinon, elle ne s'allume pas et la LED rouge s'allume.   

Il est également possible d'activer un script depuis la _partie Admin_ de l'**interface web** permettant d'**ajouter un nouveau badge**. 

#### L'interface web

Elle nécessite _obligatoirement_ une connexion.   
Une fois connecté, on distigue deux rôles : simple **utilisateur**, ou **administrateur**.   

L'utilisateur peut : 
- **Ouvrir** la serrure si un badge lui est associé
- Voir les **logs** d'ouverture de la serrure

L'administrateur peut : 
- **Ouvrir** la serrure si un badge lui est associé
- Voir les **logs** d'ouverture de la serrure
- Ajouter un **nouveau badge**, une fois la fonctionnalité activé, la serrure attend le passage d'un badge
- Ajouter un **nouvel utilisateur** en lui assignant un badge libre s'il le veut
- _Modifier_ un utilisateur et son badge
- _Supprimer_ un utilisateur
- _Supprimer_ un badge

#### L'API

L'API dispose de plusieurs adresses :

| URL                                   | Fonctionnalité                        | Requis |
| ---                                   | ---                                   | --- |
| **/open/**_badge_uid_                 | Permet d'ouvrir la serrure            | Être un **utilisateur** connu et disposant d'un **badge** |
| **/add_uid/**_badge_uid_              | Permet d'ajouter un badge             | Seule la **serrure** peut faire cela (accessible via la partie Admin de l'interface web) |
| **/send_log/**_badge_uid_/_status_    | Ajoute un log d'ouverture             | Être un **utilisateur** connu. Toujours associé à l'ouverture de la serrure |
| **/get_logs/**                        | Permet de récupérer tous les logs     | Être un **utilisateur** connu |

Pour toutes les urls, il y a une authentification, de manière à **sécuriser** l'accès à la serrure et à ses données.
