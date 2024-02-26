<?php 
function connect()
{
    // $host= '192.168.210.40';
    // $db = 'Vision';  #'IOTDatabase'
    // $user = 'postgres';
    // $password = "2Smx'P?8[#RA\#9Z";
    
    $host= 'localhost';
    $db = 'vision';
    $user = 'postgres';
    $password = "Lu090819@";
    $pdo = null;
    try
    {
        $dsn = "pgsql:host=$host;port=5432;dbname=$db;";
        // make a database connection
        return new PDO($dsn, $user, $password, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);        
    }
    catch (PDOException $e) 
    {
        die($e->getMessage());
    }
   
}


?>