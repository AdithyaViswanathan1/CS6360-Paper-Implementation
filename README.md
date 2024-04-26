# An Overview of SQL Query Correctness on Incomplete Databases

> ### Implementation-Flavor Project for CS 6360.001 Spring 2024
### *Arturo Yundt-Pacheco, Harshal Patel, Adithya Viswanathan, George Hamad, Donavin Sip (Team 14)*

Our group explored the findings in “Making SQL Queries Correct on Incomplete Databases,” which was written by Paolo Guagliardo and Leonid Libkin (PODS 2016). The algorithms, methods, and solutions presented in this paper offers us a potential solution toward minimizing, or eliminating, the presence of false positive queries in the presence of nulls within a database. Our goal was to simulate and implement theirg findings to confirm the core systems and algorithms described in the paper by carrying out all experimental studies outlined. We achieved this by replicating and following their algorithms in addition to building a database environment similiar to the one outlined in the paper to test these discoveries. Our final report covers the topics, the technologies we used to accomplish our implementations, and the challenges we faced while working on this project throughout the semester. So, please refer to the final report for a more in-depth explanation and overall coverage of the project.

## TODO
- [ ] <Installation & Run Process here (i.e. how to get the project set-up)>
1. Install MySQL and MySQLWorkbench.
2. Create root user and password. Then update secrets.json file with your SQL credentials
3. In MySQLWorkbench, go to Server > Data Import. Select "Import from Self-Contained File" and choose the given SQL file. There will be multiple databases and multiple tables within each database. This will load the full database into your local MySQL instance.
4. In your Python environment, you will need the following packages: importlib, numpy, csv, matplotlib, pandas, mysql.connector. 

- [ ] <How to Use the Project here (i.e. how someone could try it themselves [what to do])>
- - nulls.py - creates copies of databases and inserts nulls at a given null rate into nullable attributes.

(github README formatting and syntax)
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
