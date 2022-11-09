admin user:edmariesantana
Colegio404!
host:proyecto.postgres.database.azure.com

create user appusr with encrypted password 'e4&wy%g4trs.dg74hse4';

create database appdb;

grant all privileges on database appdb to appusr;  
