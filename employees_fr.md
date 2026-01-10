# **📊 Requêtes SQL pour la Base de Données Employees**

[**📊 Requêtes SQL pour la Base de Données Employees	1**](?tab=t.0#heading=)

[🗂️ Structure du Schéma Relationnel	1](?tab=t.0#heading=)

[🚀 Tableau des 60 Requêtes SQL	2](?tab=t.0#heading=)

Ce document recense 60 requêtes SQL optimisées pour MySQL 8.0, couvrant des scénarios d'analyse, de reporting et de manipulation de données complexes.

## **🗂️ Structure du Schéma Relationnel**

Voici une représentation visuelle des relations entre les tables de la base employees.

``mermaid
erDiagram
    EMPLOYEES ||--o{ SALARIES : "a"
    EMPLOYEES ||--o{ TITLES : "a"
    EMPLOYEES ||--o{ DEPT_EMP : "travaille dans"
    EMPLOYEES ||--o{ DEPT_MANAGER : "gère"
    DEPARTMENTS ||--o{ DEPT_EMP : "contient"
    DEPARTMENTS ||--o{ DEPT_MANAGER : "est géré par"

    EMPLOYEES {
        int emp_no PK
        date birth_date
        string first_name
        string last_name
        enum gender
        date hire_date
    }

    DEPARTMENTS {
        char(4) dept_no PK
        string dept_name
    }

    SALARIES {
        int emp_no PK
        int salary
        date from_date PK
        date to_date
    }

    TITLES {
        int emp_no PK
        string title PK
        date from_date PK
        date to_date
    }

``

## **🚀 Tableau des 60 Requêtes SQL**

| \# | Tables Utilisées | Type de Requête | Description & Code SQL |
| :---- | :---- | :---- | :---- |
| **1** | employees, salaries | **Jointure Simple** | **Liste des employés avec leur salaire actuel** SELECT e.first\_name, e.last\_name, s.salary FROM employees e JOIN salaries s ON e.emp\_no \= s.emp\_no WHERE s.to\_date \= '9999-01-01'; |
| **2** | employees, dept\_emp, departments | **Jointure Multiple** | **Employés et leurs départements actuels** SELECT e.first\_name, e.last\_name, d.dept\_name FROM employees e JOIN dept\_emp de ON e.emp\_no \= de.emp\_no JOIN departments d ON de.dept\_no \= d.dept\_no WHERE de.to\_date \= '9999-01-01'; |
| **3** | employees | **Aggrégat (COUNT)** | **Nombre total d'employés par genre** SELECT gender, COUNT(\*) as count FROM employees GROUP BY gender; |
| **4** | salaries | **Aggrégat (AVG)** | **Salaire moyen global actuel** SELECT AVG(salary) as avg\_salary FROM salaries WHERE to\_date \= '9999-01-01'; |
| **5** | salaries, dept\_emp, departments | **Aggrégat \+ Jointure** | **Salaire moyen par département** SELECT d.dept\_name, AVG(s.salary) as avg\_dept\_salary FROM departments d JOIN dept\_emp de ON d.dept\_no \= de.dept\_no JOIN salaries s ON de.emp\_no \= s.emp\_no WHERE s.to\_date \= '9999-01-01' AND de.to\_date \= '9999-01-01' GROUP BY d.dept\_name; |
| **6** | employees | **Recherche Regex** | **Employés dont le nom commence par 'A' ou 'B'** SELECT \* FROM employees WHERE last\_name REGEXP '^\[AB\]'; |
| **7** | employees | **Recherche Regex** | **Prénoms contenant 'mar' insensible à la casse** SELECT \* FROM employees WHERE first\_name REGEXP '(?i)mar'; |
| **8** | salaries | **Window Function (RANK)** | **Classement des salaires actuels (Top 10\)** SELECT emp\_no, salary, RANK() OVER (ORDER BY salary DESC) as salary\_rank FROM salaries WHERE to\_date \= '9999-01-01' LIMIT 10; |
| **9** | salaries, dept\_emp | **Window Function (PARTITION)** | **Classement des salaires par département** SELECT de.dept\_no, s.emp\_no, s.salary, RANK() OVER (PARTITION BY de.dept\_no ORDER BY s.salary DESC) as dept\_rank FROM salaries s JOIN dept\_emp de ON s.emp\_no \= de.emp\_no WHERE s.to\_date \= '9999-01-01' AND de.to\_date \= '9999-01-01'; |
| **10** | titles | **Aggrégat (GROUP\_CONCAT)** | **Historique des titres par employé (concaténé)** SELECT emp\_no, GROUP\_CONCAT(title ORDER BY from\_date SEPARATOR ', ') as title\_history FROM titles GROUP BY emp\_no LIMIT 100; |
| **11** | employees | **Date Function** | **Employés embauchés il y a plus de 20 ans** SELECT \* FROM employees WHERE hire\_date \<= DATE\_SUB(CURDATE(), INTERVAL 20 YEAR); |
| **12** | salaries | **Analytique (LAG)** | **Évolution du salaire (Comparaison avec précédent)** SELECT emp\_no, from\_date, salary, LAG(salary, 1\) OVER (PARTITION BY emp\_no ORDER BY from\_date) as prev\_salary, (salary \- LAG(salary, 1\) OVER (PARTITION BY emp\_no ORDER BY from\_date)) as difference FROM salaries LIMIT 100; |
| **13** | salaries | **Analytique (LEAD)** | **Anticipation du prochain changement de salaire** SELECT emp\_no, from\_date, salary, LEAD(salary, 1\) OVER (PARTITION BY emp\_no ORDER BY from\_date) as next\_salary FROM salaries LIMIT 100; |
| **14** | dept\_manager, employees | **Jointure \+ Sous-requête** | **Managers actuels qui sont des femmes** SELECT e.first\_name, e.last\_name FROM employees e JOIN dept\_manager dm ON e.emp\_no \= dm.emp\_no WHERE dm.to\_date \= '9999-01-01' AND e.gender \= 'F'; |
| **15** | salaries | **CTE (Common Table Expression)** | **Salaire moyen actuel (calculé via CTE)** WITH CurrentSalaries AS (SELECT salary FROM salaries WHERE to\_date \= '9999-01-01') SELECT AVG(salary) FROM CurrentSalaries; |
| **16** | departments, dept\_emp, salaries | **CTE Complexe** | **Départements payant mieux que la moyenne globale** WITH DeptAvg AS (SELECT de.dept\_no, AVG(s.salary) as avg\_sal FROM dept\_emp de JOIN salaries s ON de.emp\_no \= s.emp\_no WHERE s.to\_date \= '9999-01-01' GROUP BY de.dept\_no), GlobalAvg AS (SELECT AVG(salary) as glob\_sal FROM salaries WHERE to\_date \= '9999-01-01') SELECT d.dept\_name, da.avg\_sal FROM DeptAvg da JOIN departments d ON da.dept\_no \= d.dept\_no JOIN GlobalAvg ga WHERE da.avg\_sal \> ga.glob\_sal; |
| **17** | employees | **JSON Generation** | **Créer un objet JSON pour chaque employé** SELECT JSON\_OBJECT('id', emp\_no, 'name', CONCAT(first\_name, ' ', last\_name), 'gender', gender) as emp\_json FROM employees LIMIT 10; |
| **18** | titles | **JSON Aggregation** | **Liste des titres d'un employé en tableau JSON** SELECT emp\_no, JSON\_ARRAYAGG(title) as titles\_json FROM titles GROUP BY emp\_no LIMIT 10; |
| **19** | employees, dept\_emp | **Filtrage EXISTS** | **Employés n'ayant jamais changé de département** SELECT e.first\_name, e.last\_name FROM employees e WHERE EXISTS (SELECT 1 FROM dept\_emp de WHERE de.emp\_no \= e.emp\_no GROUP BY de.emp\_no HAVING COUNT(\*) \= 1\) LIMIT 100; |
| **20** | salaries | **Window Function (DENSE\_RANK)** | **Classement dense des salaires (sans trous)** SELECT salary, DENSE\_RANK() OVER (ORDER BY salary DESC) as rank\_dense FROM salaries WHERE to\_date \= '9999-01-01' LIMIT 20; |
| **21** | employees | **Recherche Regex** | **Noms finissant par 'son' ou 'sen'** SELECT last\_name FROM employees WHERE last\_name REGEXP 's\[eo\]n$' LIMIT 50; |
| **22** | dept\_emp | **Aggrégat Temporel** | **Nombre d'embauches par année** SELECT YEAR(from\_date) as hire\_year, COUNT(\*) FROM dept\_emp GROUP BY hire\_year ORDER BY hire\_year; |
| **23** | salaries | **Window Function (Running Total)** | **Cumul des salaires versés par employé (historique)** SELECT emp\_no, from\_date, salary, SUM(salary) OVER (PARTITION BY emp\_no ORDER BY from\_date) as running\_total\_paid FROM salaries LIMIT 100; |
| **24** | employees, titles | **Self Join (Simulation)** | **Employés ayant le même titre en même temps (Logique complexe)** SELECT t1.emp\_no as Emp1, t2.emp\_no as Emp2, t1.title FROM titles t1 JOIN titles t2 ON t1.title \= t2.title AND t1.emp\_no \< t2.emp\_no WHERE t1.to\_date \= '9999-01-01' AND t2.to\_date \= '9999-01-01' LIMIT 50; |
| **25** | salaries | **Window Frame** | **Moyenne mobile du salaire sur 3 périodes** SELECT emp\_no, from\_date, salary, AVG(salary) OVER (PARTITION BY emp\_no ORDER BY from\_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving\_avg FROM salaries LIMIT 100; |
| **26** | dept\_manager | **Aggrégat** | **Durée moyenne de mandat d'un manager (jours)** SELECT AVG(DATEDIFF(IF(to\_date='9999-01-01', CURDATE(), to\_date), from\_date)) as avg\_days\_as\_manager FROM dept\_manager; |
| **27** | employees | **Analytique (NTILE)** | **Répartition des employés en 4 quartiles par âge** SELECT emp\_no, birth\_date, NTILE(4) OVER (ORDER BY birth\_date) as age\_quartile FROM employees LIMIT 100; |
| **28** | salaries | **Recherche Ecart type** | **Salaires suspects (\> 3 écarts types de la moyenne)** WITH Stats AS (SELECT AVG(salary) as avg\_sal, STDDEV(salary) as std\_dev FROM salaries WHERE to\_date \= '9999-01-01') SELECT s.emp\_no, s.salary FROM salaries s, Stats st WHERE s.to\_date \= '9999-01-01' AND s.salary \> (st.avg\_sal \+ 3 \* st.std\_dev); |
| **29** | employees | **Regex Complexe** | **Prénoms avec 2 voyelles consécutives** SELECT first\_name FROM employees WHERE first\_name REGEXP '\[aeiou\]{2}' LIMIT 50; |
| **30** | dept\_emp, departments | **Pivot (Case When)** | **Pivot: Nombre d'employés par département (Colonnes)** SELECT SUM(CASE WHEN dept\_no \= 'd001' THEN 1 ELSE 0 END) as Marketing, SUM(CASE WHEN dept\_no \= 'd002' THEN 1 ELSE 0 END) as Finance FROM dept\_emp WHERE to\_date \= '9999-01-01'; |
| **31** | titles | **CTE Récursive (Simulation)** | **Générer une série de dates (pour combler les trous)** WITH RECURSIVE DateSeries AS (SELECT '2000-01-01' as d UNION ALL SELECT DATE\_ADD(d, INTERVAL 1 YEAR) FROM DateSeries WHERE d \< '2010-01-01') SELECT \* FROM DateSeries; |
| **32** | employees | **Manipulation de chaînes** | **Initiales des employés** SELECT CONCAT(LEFT(first\_name, 1), '.', LEFT(last\_name, 1), '.') as initials FROM employees LIMIT 50; |
| **33** | salaries, employees | **Window (First Value)** | **Salaire d'embauche vs Salaire actuel** SELECT emp\_no, salary, FIRST\_VALUE(salary) OVER (PARTITION BY emp\_no ORDER BY from\_date) as starting\_salary FROM salaries WHERE to\_date \= '9999-01-01' LIMIT 50; |
| **34** | dept\_emp | **Aggrégat avec ROLLUP** | **Total employés par département avec sous-totaux** SELECT dept\_no, COUNT(\*) FROM dept\_emp WHERE to\_date \= '9999-01-01' GROUP BY dept\_no WITH ROLLUP; |
| **35** | employees | **JSON Extraction** | **Extraire infos d'un JSON généré (Simulation)** SELECT JSON\_EXTRACT(JSON\_OBJECT('name', first\_name), '$.name') as name\_extracted FROM employees LIMIT 10; |
| **36** | salaries | **Analytique (Percent Rank)** | **Rang centile du salaire** SELECT emp\_no, salary, PERCENT\_RANK() OVER (ORDER BY salary) as percentile FROM salaries WHERE to\_date \= '9999-01-01' LIMIT 100; |
| **37** | employees, dept\_emp | **Anti-Join (Left Join NULL)** | **Employés sans assignation de département active (Théorique)** SELECT e.emp\_no FROM employees e LEFT JOIN dept\_emp de ON e.emp\_no \= de.emp\_no AND de.to\_date \= '9999-01-01' WHERE de.dept\_no IS NULL; |
| **38** | salaries | **Aggrégat (MIN/MAX)** | **Écart de salaire min/max par employé** SELECT emp\_no, MAX(salary) \- MIN(salary) as salary\_growth\_range FROM salaries GROUP BY emp\_no LIMIT 100; |
| **39** | dept\_manager | **CTE \+ Window** | **Managers successifs par département** WITH Managers AS (SELECT dept\_no, emp\_no, from\_date, to\_date FROM dept\_manager) SELECT dept\_no, emp\_no, LAG(emp\_no) OVER (PARTITION BY dept\_no ORDER BY from\_date) as prev\_manager FROM Managers; |
| **40** | employees | **Regex Boundary** | **Noms commençant et finissant par la même lettre** SELECT first\_name FROM employees WHERE first\_name REGEXP '^(.).\*\\\\1$' LIMIT 20; |
| **41** | salaries | **Mathématiques** | **Salaire modulo 1000 (Répartition des restes)** SELECT salary % 1000 as remainder, COUNT(\*) FROM salaries WHERE to\_date \= '9999-01-01' GROUP BY remainder ORDER BY remainder; |
| **42** | titles, dept\_emp | **Jointure Complexe** | **Titre actuel vs Département actuel** SELECT t.title, d.dept\_name, COUNT(\*) FROM titles t JOIN dept\_emp de ON t.emp\_no \= de.emp\_no JOIN departments d ON de.dept\_no \= d.dept\_no WHERE t.to\_date \= '9999-01-01' AND de.to\_date \= '9999-01-01' GROUP BY t.title, d.dept\_name; |
| **43** | employees | **Aggrégat (Date)** | **Employés nés le week-end** SELECT \* FROM employees WHERE DAYOFWEEK(birth\_date) IN (1, 7\) LIMIT 50; |
| **44** | salaries | **Analytique (CUME\_DIST)** | **Distribution cumulative des salaires** SELECT salary, CUME\_DIST() OVER (ORDER BY salary) as cum\_dist FROM salaries WHERE to\_date \= '9999-01-01' LIMIT 100; |
| **45** | dept\_emp | **Window Count** | **Nombre de changements de département par employé** SELECT emp\_no, COUNT(\*) OVER (PARTITION BY emp\_no) as dept\_changes FROM dept\_emp LIMIT 100; |
| **46** | employees | **Formatage JSON** | **Pretty Print d'un employé (Formatage)** SELECT JSON\_PRETTY(JSON\_OBJECT('id', emp\_no, 'dates', JSON\_OBJECT('birth', birth\_date, 'hire', hire\_date))) FROM employees LIMIT 1; |
| **47** | salaries | **Mise à jour (Safe Update)** | **Augmentation théorique de 10% (Select)** SELECT emp\_no, salary, salary \* 1.10 as potential\_salary FROM salaries WHERE to\_date \= '9999-01-01'; |
| **48** | employees, dept\_emp | **Union** | **Liste unifiée Managers et Employés (avec type)** SELECT emp\_no, 'Manager' as type FROM dept\_manager WHERE to\_date \= '9999-01-01' UNION SELECT emp\_no, 'Employee' FROM dept\_emp WHERE to\_date \= '9999-01-01' LIMIT 100; |
| **49** | titles | **Regex Alternation** | **Titres contenant Engineer ou Staff** \`SELECT DISTINCT title FROM titles WHERE title REGEXP 'Engineer |
| **50** | salaries | **CTE \+ Join** | **Employés au salaire maximal de leur département** WITH MaxDepSal AS (SELECT de.dept\_no, MAX(s.salary) as max\_sal FROM dept\_emp de JOIN salaries s ON de.emp\_no \= s.emp\_no WHERE s.to\_date \= '9999-01-01' GROUP BY de.dept\_no) SELECT de.emp\_no, de.dept\_no, s.salary FROM dept\_emp de JOIN salaries s ON de.emp\_no \= s.emp\_no JOIN MaxDepSal mds ON de.dept\_no \= mds.dept\_no AND s.salary \= mds.max\_sal WHERE s.to\_date \= '9999-01-01'; |
| **51** | employees | **Tri Aléatoire** | **Échantillon aléatoire de 5 employés** SELECT \* FROM employees ORDER BY RAND() LIMIT 5; |
| **52** | salaries | **Opérateur Bitwise** | **Salaires pairs uniquement** SELECT emp\_no, salary FROM salaries WHERE (salary & 1\) \= 0 LIMIT 20; |
| **53** | dept\_emp | **Group By Having** | **Employés ayant travaillé dans plus de 2 départements** SELECT emp\_no, COUNT(DISTINCT dept\_no) as nb\_depts FROM dept\_emp GROUP BY emp\_no HAVING nb\_depts \> 2; |
| **54** | employees | **Full Text (Simulation)** | **Recherche approximative (Soundex)** SELECT \* FROM employees WHERE SOUNDEX(last\_name) \= SOUNDEX('Schwarzenegger'); |
| **55** | salaries | **Analytique (Row Number)** | **Suppression de doublons (Simulation sélection)** WITH Duplicates AS (SELECT \*, ROW\_NUMBER() OVER(PARTITION BY emp\_no, from\_date ORDER BY to\_date DESC) as rn FROM salaries) SELECT \* FROM Duplicates WHERE rn \> 1; |
| **56** | departments | **JSON Array** | **Liste des départements en tableau JSON** SELECT JSON\_ARRAYAGG(dept\_name) FROM departments; |
| **57** | employees | **Calcul d'âge** | **Âge actuel des employés** SELECT emp\_no, TIMESTAMPDIFF(YEAR, birth\_date, CURDATE()) as age FROM employees LIMIT 50; |
| **58** | salaries | **Histogramme (CASE)** | **Catégorisation des salaires (Low, Med, High)** SELECT CASE WHEN salary \< 50000 THEN 'Low' WHEN salary BETWEEN 50000 AND 100000 THEN 'Medium' ELSE 'High' END as category, COUNT(\*) FROM salaries WHERE to\_date \= '9999-01-01' GROUP BY category; |
| **59** | titles | **Regex Character Class** | **Titres sans chiffres** SELECT DISTINCT title FROM titles WHERE title NOT REGEXP '\[0-9\]'; |
| **60** | all tables | **Meta Data** | **Taille des tables en Mo (Requête Admin)** SELECT table\_name, round(((data\_length \+ index\_length) / 1024 / 1024), 2\) as size\_mb FROM information\_schema.tables WHERE table\_schema \= 'employees'; |

*Note: Les requêtes sont conçues pour des environnements MariaDB. Certaines fonctionnalités peuvent ne pas être disponibles dans les versions antérieures ou d'autres systèmes de gestion de bases de données.*