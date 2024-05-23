# Programme de gestion des contentieux
Ce script python permet d'ajouter une note bloquante de type "Retard > 35 J" sur les comptes des lecteurs ayant des documents empruntés avec un retard supérieur à 35 jours.
Il permet aussi de lever les notes blocantes de type "Retard > 35 J", "Contact 1 suivi de contentieux", "Contact 2 suivi de contentieux" et "Contact 3 suivi de contentieux" sur tous les comptes des lecteurs n'ayant plus de documents en retard.
## Ajout de la note bloquante
Pour identifier les comptes à bloquer le programme s'appuie sur le rapport analytique suivant : /shared/Bordeaux NZ 33PUDB_NETWORK/prod/Services aux publics/Gestion des retards et des contentieux/Pour Automatisation/Lecteurs Retards 35j a bloquer SQL". 
Le rapport extrait le code de l'institution et l'identifiant des lecteurs (Primary Id) ayant :
 - des prêts actifs avec une date de retour vide
 - un retard de plus de 35 j (date du jour - date de retour prévue > 35 j). 
 - pas de note bloquante de type ""Retard > 35 J"
```SQL
SELECT 
   A.Institution saw_0,
   A.User_id saw_1,
   A.BID saw_2,
   A.BIB saw_3
 FROM ( SELECT
   "Fulfillment"."Institution"."Institution Code" Institution,
   "Fulfillment"."Borrower Details"."User Id" User_id,
   "Fulfillment"."Borrower Details"."Primary Identifier" BID,
   "Fulfillment"."Item Location at Time of Loan"."Library Name" BIB
FROM "Fulfillment"
WHERE
  ((TimestampDiff(SQL_TSI_DAY,"Fulfillment"."Due Date"."Due Date",CURRENT_DATE) >= 35) 
  AND ("Return Date"."Return Date" IS NULL) 
  AND ("Loan Details"."Loan Status" = 'Active') 
  )) A LEFT JOIN (
  SELECT
   "Users"."User Details"."User Id" User_id,
   "Users"."Institution"."Institution Code" Institution
FROM "Users"
WHERE
(("Block"."Block Status" = 'Active') AND ("Block"."Block Description" = 'Retard > 35 jours'))
) B ON A.User_id = B.User_id AND A.Institution = B.Institution
 WHERE 
B.User_id is NULL
 ORDER BY saw_0, saw_1, saw_2
```
Il execute le rapport et ventile tous les comptes des lecteurs en fonction de l'institution dans laquelle ils sont considérés comme en grand retard.
Instititution par institution , il parcourt la liste des lecteurs et ajoute la note blocante sur le compte via les API GET et Update user.
## Nettoyage des notes bloquantes
Pour identifier les comptes à débloquer le programme s'appuie sur le rapport analytique suivant : /shared/Bordeaux NZ 33PUDB_NETWORK/prod/Services aux publics/Gestion des retards et des contentieux/Pour Automatisation/Lecteurs Retards 35j a debloquer SQL". 
Le rapport extrait le code de l'institution et l'identifiant des lecteurs (Primary Id) ayant :
 - une note bloquante de type ""Retard > 35 J"
 - pas de prêts retards de plus de 35 j (date du jour - date de retour prévue > 35 j). 
```SQL
LECT 
   A.Institution saw_0,
   A.User_id saw_1,
   A.BID saw_2,
   A.BIB saw_3
 FROM (
  SELECT
   "Users"."User Details"."User Id" User_id,
   "Users"."User Details"."Primary Identifier" BID,
   "Users"."Institution"."Institution Code" Institution,
   'BIB' BIB
FROM "Users"
WHERE
(("Block"."Block Status" = 'Active') AND ("Block"."Block Description" = 'Retard > 35 jours'))
) A LEFT JOIN ( SELECT
   "Fulfillment"."Borrower Details"."User Id" User_id,
   "Fulfillment"."Institution"."Institution Code" Institution
FROM "Fulfillment"
WHERE
  ((TimestampDiff(SQL_TSI_DAY,"Fulfillment"."Due Date"."Due Date",CURRENT_DATE) >= 35) 
  AND ("Return Date"."Return Date" IS NULL) 
  AND ("Loan Details"."Loan Status" = 'Active') 
  )) B ON A.User_id = B.User_id AND A.Institution = B.Institution
 WHERE 
    B.User_id is NULL
 ORDER BY saw_0, saw_1, saw_2
```
Il execute le rapport et ventile tous les comptes des lecteurs en fonction de l'institution dans laquelle ils possèdent une note bloquante.
Instititution par institution , il parcourt la liste des lecteurs et supprime les notes de contentieux via les API GET et Update user.


