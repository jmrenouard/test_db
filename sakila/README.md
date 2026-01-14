# 🎬 Sakila Sample Database

This sample database is a modified version of the [Sakila Spatial Database](https://dev.mysql.com/doc/index-other.html), optimized for diverse MySQL and MariaDB versions.

## ✨ Key Enhancements

- **Engine Compatibility**: Fine-tuned for modern InnoDB features.
- **Conditional Indexes**:
  - **FULLTEXT**: Automatically added for MySQL 5.6+ / MariaDB environments.
  - **SPATIAL**: GEOMETRY columns and SPATIAL indexes are added conditionally for MySQL 5.7+ / MariaDB environments.

## 🚀 Installation

To import the Sakila database:

```bash
mysql < sakila-mv-schema.sql
mysql < sakila-mv-data.sql
```
