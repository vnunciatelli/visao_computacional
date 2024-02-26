<?php
require_once "conection.php";
$pdo = connect();

$data = [
    'qtd_pessoas_detectadas' => $_POST['total_pessoas'],
    'data_hora' => $_POST['data_hora']
];
$sql = "INSERT INTO vision_table (qtd_pessoas_detectadas, data_hora) VALUES (:qtd_pessoas_detectadas, :data_hora)";
$stmt= $pdo->prepare($sql);
$stmt->execute($data);

?>